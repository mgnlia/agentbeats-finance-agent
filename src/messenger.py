from a2a.client import A2AClient
from a2a.types import Message
import httpx

class Messenger:
    async def talk_to_agent(self, message: Message, url: str) -> str:
        async with httpx.AsyncClient() as http:
            client = await A2AClient.get_client_from_agent_card_url(http, url)
            response = await client.send_message(message)
            return str(response)
