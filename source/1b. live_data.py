import pandas as pd
import asyncio
import time
import statsbombapi
from prometheus_client import Counter, start_http_server, Gauge, Histogram

# -----------------------------
# Global State
# -----------------------------
api = statsbombapi.StatsbombPublic()
MATCH_BUFFER = []
all_event_dfs = []  # Store all processed events
PROCESSED_MATCH_IDS = set()
BUFFER_SIZE = 5
SLEEP_TIME = 0.2  # simulate I/O delay

dataframe_decoder = statsbombapi.decoders.CompositeDecoder(
    statsbombapi.decoders.JsonDecoder(),
    statsbombapi.decoders.UniformDecoder(pd.DataFrame)
)
df_client = statsbombapi.StatsbombPublic(decoder=dataframe_decoder)

# # Prometheus metrics
# matches_processed = Counter('matches_processed_total', 'Total matches processed in batches')
# batches_processed = Counter('batches_processed_total', 'Total batches processed')

# Prometheus metrics
matches_processed = Counter('matches_processed_total', 'Total matches processed in batches')
batches_processed = Counter('batches_processed_total', 'Total batches processed')
match_buffer_size = Gauge('match_buffer_size', 'Current size of the match buffer')
processing_duration = Histogram('match_batch_processing_seconds', 'Time spent processing a batch of matches')

match_buffer_size.set(len(MATCH_BUFFER))

# Start Prometheus metrics server on port 8000
start_http_server(8000)

# # -----------------------------
# # Async Batch Processor
# # -----------------------------
# async def process_match_batch(batch):
#     await asyncio.sleep(SLEEP_TIME)  # simulate processing time
#     match_ids = [m.id for m in batch]
#     print(f"Processing batch: {match_ids}")
    
#     batch_dfs = []

#     for match_id in match_ids:
#         try:
#             df = df_client.events(match_id=match_id)
#             df['match_id'] = match_id
#             batch_dfs.append(df)
#         except Exception as e:
#             print(f"Error processing match {match_id}: {e}")

#     if batch_dfs:
#         combined_df = pd.concat(batch_dfs, ignore_index=True)
#         all_event_dfs.append(combined_df)
#         print(f"Combined events from {len(match_ids)} matches. Final shape: {combined_df.shape}")
#     else:
#         print("No events processed in this batch.")

#     # Update metrics
#     matches_processed.inc(len(match_ids))
#     batches_processed.inc()

# # -----------------------------
# # Match Streamer
# # -----------------------------
# async def stream_matches(matches):
#     global MATCH_BUFFER
#     for match in matches:
#         if match.id not in PROCESSED_MATCH_IDS:
#             MATCH_BUFFER.append(match)
#             PROCESSED_MATCH_IDS.add(match.id)

#         if len(MATCH_BUFFER) >= BUFFER_SIZE:
#             await process_match_batch(MATCH_BUFFER)
#             MATCH_BUFFER = []

#     # Final leftover batch
#     if MATCH_BUFFER:
#         await process_match_batch(MATCH_BUFFER)
#         MATCH_BUFFER = []

@processing_duration.time()
async def process_match_batch(batch):
    await asyncio.sleep(SLEEP_TIME)
    match_ids = [m.id for m in batch]
    print(f"Processing batch: {match_ids}")
    
    batch_dfs = []

    for match_id in match_ids:
        try:
            df = df_client.events(match_id=match_id)
            df['match_id'] = match_id
            batch_dfs.append(df)
        except Exception as e:
            print(f"Error processing match {match_id}: {e}")

    if batch_dfs:
        combined_df = pd.concat(batch_dfs, ignore_index=True)
        all_event_dfs.append(combined_df)
        print(f"Combined events from {len(match_ids)} matches. Final shape: {combined_df.shape}")
    else:
        print("No events processed in this batch.")

    matches_processed.inc(len(match_ids))
    batches_processed.inc()

async def stream_matches(matches):
    global MATCH_BUFFER
    for match in matches:
        if match.id not in PROCESSED_MATCH_IDS:
            MATCH_BUFFER.append(match)
            PROCESSED_MATCH_IDS.add(match.id)

        match_buffer_size.set(len(MATCH_BUFFER))

        if len(MATCH_BUFFER) >= BUFFER_SIZE:
            await process_match_batch(MATCH_BUFFER)
            MATCH_BUFFER = []
            match_buffer_size.set(0)

# -----------------------------
# Fetch New Matches Only
# -----------------------------
async def fetch_new_matches():
    competitions = api.competitions()
    desired_season_ids = [1, 2]#, 4, 21, 22, 23, 24, 25, 26, 27, 37, 38, 39, 40, 41, 42, 86, 90, 278]
    comps = [c for c in competitions if c.competition_id == 11 and c.season_id in desired_season_ids]

    if not comps:
        print("No matching competitions found!")
        return []

    all_matches = []
    for comp in comps:
        try:
            matches = await asyncio.to_thread(api.matches, comp.competition_id, comp.season_id)
            new_matches = [m for m in matches if m.id not in PROCESSED_MATCH_IDS]
            all_matches.extend(new_matches)
        except Exception as e:
            print(f"Failed to load matches for comp {comp.competition_id}, season {comp.season_id}: {e}")

    return all_matches

# -----------------------------
# Main Streaming Loop
# -----------------------------
async def main_streaming_loop():
    while True:
        new_matches = await fetch_new_matches()
        if new_matches:
            print(f"Found {len(new_matches)} new matches.")
            await stream_matches(new_matches)
        else:
            print("No new matches. Sleeping...")
        await asyncio.sleep(5)

# -----------------------------
# Run
# -----------------------------
if __name__ == "__main__":
    try:
        asyncio.run(main_streaming_loop())
    except KeyboardInterrupt:
        print("Streaming stopped.")
        # Optional: Combine and save data
        if all_event_dfs:
            final_df = pd.concat(all_event_dfs, ignore_index=True)
            final_df.to_csv("/mnt/block/data/final_datasets/streamed_data.csv", index=False)
            print(f"Saved {len(final_df)} events to CSV.")
