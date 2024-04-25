import abc
import httpx


class ResultsObserver(abc.ABC):
    @abc.abstractmethod
    def observe(self, data: bytes) -> None:
        ...


async def do_reliable_request(
    url: str, observer: ResultsObserver, max_retries=5, timeout=10.0
) -> None:
    async with httpx.AsyncClient(timeout=timeout) as client:
        attempt = 0
        while attempt < max_retries:
            try:
                response = await client.get(url)
                response.raise_for_status()
                data = response.content
                observer.observe(data)
                return

            except (httpx.HTTPStatusError, httpx.TimeoutException, httpx.NetworkError) as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                attempt += 1
                if attempt == max_retries:
                    raise Exception(
                        f"Failed to fetch data after {max_retries} attempts"
                    ) from e
