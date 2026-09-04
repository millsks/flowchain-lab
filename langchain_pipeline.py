import sys
from dataclasses import asdict
from langchain_core.runnables import RunnableBranch, RunnableLambda

from order_lookup import lookup_order, parse_command

def serialize(order):
    if order is None:
        return {"found": False}
    return {"found": True, "order": asdict(order)}


health_check = RunnableLambda(lambda input: {"status": "ok"} if input == "health" else None)
order_lookup = (
    RunnableLambda(parse_command)
    | RunnableLambda(lookup_order)
    | RunnableLambda(serialize)
)
pipeline = (
    RunnableBranch(
        (
            lambda input: input == "health",
            health_check,
        ),
        order_lookup,
    )
)

if __name__ == "__main__":
    args = sys.argv[1:]
    request = args[0] if args else "1002"
    print(f"Running request {request}...")
    print(pipeline.invoke(request))