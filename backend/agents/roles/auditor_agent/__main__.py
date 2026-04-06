# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Main for the auditor agent."""

from collections.abc import Sequence
from absl import app
from agents.roles.auditor_agent.agent import root_agent
from agents.common import server

AGENT_AUDITOR_PORT = 8004

class AuditorAgentExecutor:
    """Simple executor for auditor agent."""
    
    def __init__(self, supported_extensions=None):
        self.agent = root_agent
        self.supported_extensions = supported_extensions or []

def main(argv: Sequence[str]) -> None:
    agent_card = server.load_local_agent_card(__file__)
    server.run_agent_blocking(
        port=AGENT_AUDITOR_PORT,
        agent_card=agent_card,
        executor=AuditorAgentExecutor(agent_card.capabilities.extensions),
        rpc_url="/a2a/auditor_agent",
    )

if __name__ == "__main__":
    app.run(main)