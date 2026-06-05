import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:8080").rstrip("/")
PAYMENT_URL = os.getenv("PAYMENT_SERVICE_URL", "http://localhost:8004").rstrip("/")

APP_SERVICES = [
    "user-service",
    "product-service",
    "order-service",
    "payment-service",
    "notification-service",
]
DATA_SERVICES = ["user-db", "product-db", "order-db", "notification-db", "redis", "rabbitmq"]
EDGE_SERVICES = ["nginx", "prometheus", "grafana"]
ALL_SERVICES = DATA_SERVICES + APP_SERVICES + EDGE_SERVICES

DEPENDENT_RESTARTS = {
    "user-db": ["user-service"],
    "product-db": ["product-service"],
    "order-db": ["order-service"],
    "notification-db": ["notification-service"],
    "redis": ["product-service"],
    "rabbitmq": ["order-service", "notification-service"],
}


@dataclass(frozen=True)
class Scenario:
    key: str
    category: str
    title: str
    symptom: str
    restore_hint: str
    apply: Callable[[argparse.Namespace], None]
    restore: Callable[[argparse.Namespace], None]


def run(args: list[str], options: argparse.Namespace, *, check: bool = True, capture: bool = False) -> subprocess.CompletedProcess:
    if options.verbose or options.dry_run:
        print("$ " + " ".join(args))
    if options.dry_run:
        return subprocess.CompletedProcess(args, 0, "", "")

    completed = subprocess.run(
        args,
        cwd=ROOT,
        check=False,
        capture_output=capture,
        text=True,
    )
    if check and completed.returncode != 0:
        if completed.stdout:
            print(completed.stdout.strip())
        if completed.stderr:
            print(completed.stderr.strip(), file=sys.stderr)
        raise SystemExit(completed.returncode)
    return completed


def compose(options: argparse.Namespace, *args: str, check: bool = True, capture: bool = False) -> subprocess.CompletedProcess:
    return run(["docker", "compose", *args], options, check=check, capture=capture)


def docker(options: argparse.Namespace, *args: str, check: bool = True, capture: bool = False) -> subprocess.CompletedProcess:
    return run(["docker", *args], options, check=check, capture=capture)


def container_id(service: str, options: argparse.Namespace) -> str:
    result = compose(options, "ps", "-q", service, capture=True)
    cid = result.stdout.strip()
    if not cid:
        raise SystemExit(f"No container found for service: {service}")
    return cid


def service_network(service: str, options: argparse.Namespace) -> str:
    networks = container_networks(service, options)
    for network in networks:
        if network.endswith("_lab-net") or network.endswith("-lab-net"):
            return network
    if networks:
        return networks[0]
    raise SystemExit(f"No Docker network found for service: {service}")


def container_networks(service: str, options: argparse.Namespace) -> list[str]:
    cid = container_id(service, options)
    result = docker(
        options,
        "inspect",
        cid,
        "--format",
        "{{range $name, $_ := .NetworkSettings.Networks}}{{println $name}}{{end}}",
        capture=True,
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def compose_network(options: argparse.Namespace) -> str:
    result = docker(options, "network", "ls", "--format", "{{.Name}}", capture=True)
    networks = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    for network in networks:
        if network.endswith("_lab-net") or network.endswith("-lab-net"):
            return network
    raise SystemExit("Could not find the Compose lab network.")


def ensure_network_connected(service: str, network: str, options: argparse.Namespace) -> None:
    cid_result = compose(options, "ps", "-q", service, check=False, capture=True)
    cid = cid_result.stdout.strip()
    if not cid:
        return
    if network in container_networks(service, options):
        return
    docker(options, "network", "connect", "--alias", service, network, cid, check=False)


def container_is_paused(cid: str, options: argparse.Namespace) -> bool:
    result = docker(options, "inspect", cid, "--format", "{{.State.Paused}}", check=False, capture=True)
    return result.returncode == 0 and result.stdout.strip().lower() == "true"


def http_json(method: str, url: str, payload: dict | None = None, timeout: float = 10) -> tuple[int, str]:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={"Content-Type": "application/json", "X-Request-ID": "fault-lab-cli"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        body = response.read().decode("utf-8", errors="replace")
        return response.status, body


def set_payment_mode(mode: str, options: argparse.Namespace) -> None:
    urls = [
        f"{GATEWAY_URL}/api/payments/test-controls/payment-mode",
        f"{PAYMENT_URL}/test-controls/payment-mode",
    ]
    last_error: Exception | None = None
    for url in urls:
        print(f"POST {url} mode={mode}")
        if options.dry_run:
            return
        try:
            status, body = http_json("POST", url, {"mode": mode})
            print(f"{status} {body}")
            return
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_error = exc
            print(f"request failed: {exc}")
    raise SystemExit(f"Could not set payment mode to {mode}: {last_error}")


def stop_service(service: str) -> Callable[[argparse.Namespace], None]:
    return lambda options: compose(options, "stop", service)


def start_service(service: str) -> Callable[[argparse.Namespace], None]:
    def _start(options: argparse.Namespace) -> None:
        compose(options, "up", "-d", service)
        for dependent in DEPENDENT_RESTARTS.get(service, []):
            compose(options, "restart", dependent, check=False)

    return _start


def pause_service(service: str) -> Callable[[argparse.Namespace], None]:
    def _pause(options: argparse.Namespace) -> None:
        docker(options, "pause", container_id(service, options))

    return _pause


def unpause_service(service: str) -> Callable[[argparse.Namespace], None]:
    def _unpause(options: argparse.Namespace) -> None:
        docker(options, "unpause", container_id(service, options), check=False)

    return _unpause


def disconnect_service(service: str) -> Callable[[argparse.Namespace], None]:
    def _disconnect(options: argparse.Namespace) -> None:
        cid = container_id(service, options)
        network = service_network(service, options)
        docker(options, "network", "disconnect", "-f", network, cid)

    return _disconnect


def recreate_service(service: str, *dependents: str) -> Callable[[argparse.Namespace], None]:
    def _recreate(options: argparse.Namespace) -> None:
        compose(options, "up", "-d", "--force-recreate", service)
        for dependent in dependents:
            compose(options, "restart", dependent, check=False)

    return _recreate


def flush_redis(options: argparse.Namespace) -> None:
    compose(options, "exec", "-T", "redis", "redis-cli", "FLUSHDB")


def purge_rabbitmq_queue(options: argparse.Namespace) -> None:
    compose(options, "exec", "-T", "rabbitmq", "rabbitmqctl", "purge_queue", "notification.order-events.queue", check=False)


def no_op(options: argparse.Namespace) -> None:
    print("No explicit restore action is required.")


def stop_many(*services: str) -> Callable[[argparse.Namespace], None]:
    def _stop(options: argparse.Namespace) -> None:
        for service in services:
            compose(options, "stop", service)

    return _stop


def start_many(*services: str) -> Callable[[argparse.Namespace], None]:
    def _start(options: argparse.Namespace) -> None:
        compose(options, "up", "-d", *services)

    return _start


def build_scenarios() -> dict[str, Scenario]:
    scenarios = [
        Scenario(
            "payment-decline",
            "payment",
            "Payment returns declined",
            "New orders move to payment_failed while services stay healthy.",
            "Disable the flag or run restore-all to set payment mode back to success.",
            lambda options: set_payment_mode("failure", options),
            lambda options: set_payment_mode("success", options),
        ),
        Scenario(
            "payment-timeout",
            "payment",
            "Payment dependency times out",
            "Order creation waits for payment and then ends as payment_failed; latency grows.",
            "Disable the flag or run restore-all to set payment mode back to success.",
            lambda options: set_payment_mode("timeout", options),
            lambda options: set_payment_mode("success", options),
        ),
        Scenario(
            "payment-random",
            "payment",
            "Payment becomes non-deterministic",
            "Some orders are paid and some become payment_failed.",
            "Disable the flag or run restore-all to set payment mode back to success.",
            lambda options: set_payment_mode("random", options),
            lambda options: set_payment_mode("success", options),
        ),
        Scenario(
            "payment-service-stop",
            "dependency",
            "Payment service is stopped",
            "Order-service cannot reach payment-service; orders should not crash the whole system.",
            "Start payment-service and set payment mode to success.",
            stop_service("payment-service"),
            start_service("payment-service"),
        ),
        Scenario(
            "payment-service-pause",
            "dependency",
            "Payment service hangs",
            "Payment container is paused; calls hang until order-service timeout.",
            "Unpause payment-service.",
            pause_service("payment-service"),
            unpause_service("payment-service"),
        ),
        Scenario(
            "payment-service-disconnect",
            "network",
            "Payment service is isolated from Docker network",
            "DNS may resolve, but network calls to payment-service fail.",
            "Recreate payment-service to attach it back to the Compose network.",
            disconnect_service("payment-service"),
            recreate_service("payment-service"),
        ),
        Scenario(
            "user-service-stop",
            "dependency",
            "User service is stopped",
            "Order creation cannot validate users; user API routes fail.",
            "Start user-service.",
            stop_service("user-service"),
            start_service("user-service"),
        ),
        Scenario(
            "user-service-pause",
            "dependency",
            "User service hangs",
            "User API and order user lookup requests hang or time out.",
            "Unpause user-service.",
            pause_service("user-service"),
            unpause_service("user-service"),
        ),
        Scenario(
            "user-db-stop",
            "database",
            "User database is stopped",
            "user-service readiness fails and user operations break.",
            "Start user-db and restart user-service.",
            stop_service("user-db"),
            start_service("user-db"),
        ),
        Scenario(
            "user-db-disconnect",
            "network",
            "User database is isolated from network",
            "user-service cannot connect to PostgreSQL even though the DB process is alive.",
            "Recreate user-db and restart user-service.",
            disconnect_service("user-db"),
            recreate_service("user-db", "user-service"),
        ),
        Scenario(
            "product-service-stop",
            "dependency",
            "Product service is stopped",
            "Order creation cannot validate product data; product API routes fail.",
            "Start product-service.",
            stop_service("product-service"),
            start_service("product-service"),
        ),
        Scenario(
            "product-db-stop",
            "database",
            "Product database is stopped",
            "product-service readiness fails and product API breaks.",
            "Start product-db and restart product-service.",
            stop_service("product-db"),
            start_service("product-db"),
        ),
        Scenario(
            "product-db-disconnect",
            "network",
            "Product database is isolated from network",
            "product-service cannot reach product-db and becomes not ready.",
            "Recreate product-db and restart product-service.",
            disconnect_service("product-db"),
            recreate_service("product-db", "product-service"),
        ),
        Scenario(
            "redis-stop",
            "cache",
            "Redis is stopped",
            "product-service readiness fails because Redis is a required dependency.",
            "Start Redis and restart product-service if it does not recover.",
            stop_service("redis"),
            start_service("redis"),
        ),
        Scenario(
            "redis-pause",
            "cache",
            "Redis hangs",
            "Cache operations hang and product-service readiness can degrade.",
            "Unpause Redis.",
            pause_service("redis"),
            unpause_service("redis"),
        ),
        Scenario(
            "redis-cache-flush",
            "cache",
            "Redis cache is flushed",
            "Previously cached products become MISS; application still works but cache behavior changes.",
            "No restore needed; cache warms up after product reads.",
            flush_redis,
            no_op,
        ),
        Scenario(
            "order-service-stop",
            "core",
            "Order service is stopped",
            "Order API fails while other services can remain ready.",
            "Start order-service.",
            stop_service("order-service"),
            start_service("order-service"),
        ),
        Scenario(
            "order-service-pause",
            "core",
            "Order service hangs",
            "Order API requests through gateway hang or time out.",
            "Unpause order-service.",
            pause_service("order-service"),
            unpause_service("order-service"),
        ),
        Scenario(
            "order-db-stop",
            "database",
            "Order database is stopped",
            "order-service readiness fails and orders cannot be persisted.",
            "Start order-db and restart order-service.",
            stop_service("order-db"),
            start_service("order-db"),
        ),
        Scenario(
            "rabbitmq-stop",
            "messaging",
            "RabbitMQ is stopped",
            "order-service and notification-service readiness should fail; async events cannot flow.",
            "Start RabbitMQ and restart order-service/notification-service if needed.",
            stop_service("rabbitmq"),
            start_service("rabbitmq"),
        ),
        Scenario(
            "rabbitmq-pause",
            "messaging",
            "RabbitMQ hangs",
            "AMQP calls hang; notification consumption stops while containers still exist.",
            "Unpause RabbitMQ.",
            pause_service("rabbitmq"),
            unpause_service("rabbitmq"),
        ),
        Scenario(
            "rabbitmq-disconnect",
            "network",
            "RabbitMQ is isolated from network",
            "Services cannot connect to AMQP, but RabbitMQ container can still appear alive.",
            "Recreate RabbitMQ and restart order-service/notification-service.",
            disconnect_service("rabbitmq"),
            recreate_service("rabbitmq", "order-service", "notification-service"),
        ),
        Scenario(
            "rabbitmq-queue-purge",
            "messaging",
            "Pending notification events are purged",
            "Messages waiting in notification queue are dropped; notifications may never be created.",
            "No automatic recovery for purged messages; recreate the business event or reset data.",
            purge_rabbitmq_queue,
            no_op,
        ),
        Scenario(
            "notification-service-stop",
            "messaging",
            "Notification consumer is stopped",
            "Orders can be created, but notifications remain pending in RabbitMQ.",
            "Start notification-service and wait for queued events to be consumed.",
            stop_service("notification-service"),
            start_service("notification-service"),
        ),
        Scenario(
            "notification-service-pause",
            "messaging",
            "Notification consumer hangs",
            "Order events accumulate or remain unacked; notification API may hang.",
            "Unpause notification-service.",
            pause_service("notification-service"),
            unpause_service("notification-service"),
        ),
        Scenario(
            "notification-db-stop",
            "database",
            "Notification database is stopped",
            "notification-service cannot persist consumed events and readiness fails.",
            "Start notification-db and restart notification-service.",
            stop_service("notification-db"),
            start_service("notification-db"),
        ),
        Scenario(
            "gateway-stop",
            "gateway",
            "Nginx gateway is stopped",
            "Public UI and /api routes at port 8080 are unavailable while internal services may work.",
            "Start nginx.",
            stop_service("nginx"),
            start_service("nginx"),
        ),
        Scenario(
            "prometheus-stop",
            "observability",
            "Prometheus is stopped",
            "Metrics collection stops and Grafana panels backed by Prometheus fail.",
            "Start Prometheus.",
            stop_service("prometheus"),
            start_service("prometheus"),
        ),
        Scenario(
            "grafana-stop",
            "observability",
            "Grafana is stopped",
            "Dashboards are unavailable while metrics may still be collected by Prometheus.",
            "Start Grafana.",
            stop_service("grafana"),
            start_service("grafana"),
        ),
        Scenario(
            "observability-stop",
            "observability",
            "Prometheus and Grafana are stopped",
            "The application works, but monitoring and dashboards are unavailable.",
            "Start Prometheus and Grafana.",
            stop_many("grafana", "prometheus"),
            start_many("prometheus", "grafana"),
        ),
    ]
    return {scenario.key: scenario for scenario in scenarios}


SCENARIOS = build_scenarios()


def list_scenarios(args: argparse.Namespace) -> None:
    width = max(len(key) for key in SCENARIOS)
    for key, scenario in sorted(SCENARIOS.items()):
        print(f"{key.ljust(width)}  [{scenario.category}] {scenario.title}")


def show_scenario(args: argparse.Namespace) -> None:
    scenario = require_scenario(args.flag)
    print(f"{scenario.key}")
    print(f"category: {scenario.category}")
    print(f"title: {scenario.title}")
    print(f"symptom: {scenario.symptom}")
    print(f"restore: {scenario.restore_hint}")


def enable_scenario(args: argparse.Namespace) -> None:
    scenario = require_scenario(args.flag)
    print(f"Enabling fault flag: {scenario.key}")
    scenario.apply(args)
    print(f"Expected symptom: {scenario.symptom}")
    print(f"Restore: python scripts/fault_lab.py disable {scenario.key}")


def disable_scenario(args: argparse.Namespace) -> None:
    scenario = require_scenario(args.flag)
    print(f"Disabling fault flag: {scenario.key}")
    scenario.restore(args)
    print("Restore action finished.")


def restore_all(args: argparse.Namespace) -> None:
    print("Restoring all services to the baseline running state.")
    for service in ALL_SERVICES:
        cid_result = compose(args, "ps", "-q", service, check=False, capture=True)
        cid = cid_result.stdout.strip()
        if cid and container_is_paused(cid, args):
            docker(args, "unpause", cid, check=False)

    compose(args, "up", "-d", "--remove-orphans")
    network = compose_network(args)
    for service in ALL_SERVICES:
        ensure_network_connected(service, network, args)
    for service in APP_SERVICES + EDGE_SERVICES:
        compose(args, "restart", service, check=False)
    compose(args, "up", "-d", "nginx", "prometheus", "grafana")
    wait_for_gateway(args, timeout=90)
    set_payment_mode("success", args)
    print("Baseline restore finished.")


def reset_data(args: argparse.Namespace) -> None:
    if not args.yes:
        raise SystemExit("This deletes Docker volumes. Re-run with --yes if you really want to reset data.")
    compose(args, "down", "-v")
    compose(args, "up", "-d", "--build")
    wait_for_gateway(args, timeout=180)
    set_payment_mode("success", args)
    print("Data reset finished.")


def status(args: argparse.Namespace) -> None:
    compose(args, "ps")


def smoke(args: argparse.Namespace) -> None:
    checks = [
        ("gateway", f"{GATEWAY_URL}/ready"),
        ("users", f"{GATEWAY_URL}/api/users/ready"),
        ("products", f"{GATEWAY_URL}/api/products/ready"),
        ("orders", f"{GATEWAY_URL}/api/orders/ready"),
        ("payments", f"{GATEWAY_URL}/api/payments/ready"),
        ("notifications", f"{GATEWAY_URL}/api/notifications/ready"),
        ("prometheus", "http://localhost:9090/-/ready"),
        ("grafana", "http://localhost:3000/api/health"),
    ]
    failed = False
    for name, url in checks:
        try:
            status_code, body = http_json("GET", url, timeout=5)
            print(f"{name.ljust(14)} {status_code} {body[:120].replace(chr(10), ' ')}")
        except Exception as exc:
            failed = True
            print(f"{name.ljust(14)} FAIL {exc}")
    if failed:
        raise SystemExit(1)


def wait_for_gateway(args: argparse.Namespace, timeout: float) -> None:
    if args.dry_run:
        return
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            status_code, _ = http_json("GET", f"{GATEWAY_URL}/ready", timeout=3)
            if status_code == 200:
                return
        except Exception:
            pass
        time.sleep(2)
    raise SystemExit("Gateway did not become ready in time.")


def require_scenario(key: str) -> Scenario:
    try:
        return SCENARIOS[key]
    except KeyError:
        known = ", ".join(sorted(SCENARIOS))
        raise SystemExit(f"Unknown fault flag: {key}\nKnown flags: {known}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Fault injection CLI for microservices-qa-lab.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print commands without executing them.")
    parser.add_argument("--verbose", action="store_true", help="Print Docker commands before executing them.")

    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List available fault flags.")
    list_parser.set_defaults(func=list_scenarios)

    show_parser = subparsers.add_parser("show", help="Show one fault flag.")
    show_parser.add_argument("flag")
    show_parser.set_defaults(func=show_scenario)

    enable_parser = subparsers.add_parser("enable", aliases=["apply"], help="Enable a fault flag.")
    enable_parser.add_argument("flag")
    enable_parser.set_defaults(func=enable_scenario)

    disable_parser = subparsers.add_parser("disable", aliases=["restore"], help="Disable a fault flag.")
    disable_parser.add_argument("flag")
    disable_parser.set_defaults(func=disable_scenario)

    restore_parser = subparsers.add_parser("restore-all", help="Restore all services without deleting volumes.")
    restore_parser.set_defaults(func=restore_all)

    reset_parser = subparsers.add_parser("reset-data", help="Delete volumes and rebuild the whole lab.")
    reset_parser.add_argument("--yes", action="store_true", help="Confirm destructive data reset.")
    reset_parser.set_defaults(func=reset_data)

    status_parser = subparsers.add_parser("status", help="Show docker compose status.")
    status_parser.set_defaults(func=status)

    smoke_parser = subparsers.add_parser("smoke", help="Run a quick readiness smoke check.")
    smoke_parser.set_defaults(func=smoke)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
