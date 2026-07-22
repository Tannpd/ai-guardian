// AIGuardian JavaScript SDK Client
import { createClient } from 'genlayer-js';
import { studionet } from 'genlayer-js/chains';

const CONTRACT_ADDRESS = "0x478eD5E9EE94Fb2b9E96973efbACBe3330002c56";

export async function getGuildsCount() {
  const client = createClient({ chain: studionet });
  const count = await client.readContract({
    address: CONTRACT_ADDRESS,
    functionName: "get_guilds_count",
    args: []
  });
  return Number(count);
}

export async function getGuild(guildId) {
  const client = createClient({ chain: studionet });
  const guildJsonStr = await client.readContract({
    address: CONTRACT_ADDRESS,
    functionName: "get_guild",
    args: [guildId]
  });
  return JSON.parse(guildJsonStr);
}
