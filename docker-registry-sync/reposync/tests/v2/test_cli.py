import asyncio
from concurrent.futures import ThreadPoolExecutor
import random


# Example non-blocking coroutine
async def non_blocking_task(n):
    print(f"Starting non-blocking task {n}")
    await asyncio.sleep(random.uniform(0.5, 2.0))  # Simulate async work
    #print(f"Finished non-blocking task {n}")
    return n


async def main(tasks_to_run, max_workers=10):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        loop = asyncio.get_running_loop()

        # Create tasks for all coroutines
        tasks = [
            loop.run_in_executor(executor, asyncio.run, task) for task in tasks_to_run
        ]

        # Gather and wait for all tasks to complete
        results = await asyncio.gather(*tasks)

    print("All tasks completed.")
    print("Results:", results)


asyncio.run(main([non_blocking_task(i) for i in range(50)]))
