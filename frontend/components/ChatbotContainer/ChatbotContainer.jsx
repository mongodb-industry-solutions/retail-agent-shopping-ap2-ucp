import React, { useEffect, useRef } from "react";

import MessageBubble from "../MessageBubble/MessageBubble";
import { useSelector } from "react-redux";
import { chatWithShoppingAgentAPI } from "@/lib/api";
import AgentThinking from "../MessageBubble/AgentThinking";

const ChatbotContainer = ({ journeyId, setSelectedMessage }) => {
  const messages = useSelector(state => state.Global.messages[journeyId]) || [];  
  const agentIsThinking = useSelector(state => state.MandateLedger.journeysStatus[journeyId]?.agentIsThinking) || false;
  const messagesEndRef = useRef(null);

  const handleOptionClick = async (optionId, nextMessageId, optionLabel) => {
    // Call the API with the selected option
    try {
      await chatWithShoppingAgentAPI(journeyId, optionLabel, optionId);
    } catch (error) {
      console.error("Error sending message:", error);
    }
  };
  
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div
      className="chatbotBody"
      style={{
        flex: 1,
        overflowY: "auto",
        padding: 24,
        maxWidth: 900,
        margin: "0 auto",
        width: "100%",
      }}
    >
      {messages && messages.length > 0 ? messages.map((message, index) => (
        <MessageBubble
          setSelectedMessage={setSelectedMessage}
          key={`${message.id}-${index}`}
          messageType={message.type}
          messageContent={message.content}
          messageOptions={message.messageOptions}
          onOptionClick={handleOptionClick}
          isLatest={index === messages.length - 1}
          messageDetails={
            {
            behindTheScenes: {
              summary: "Buyer/Shopping Agent received user intent",
              keyPoints: [
                "User intent captured",
                "Querying Seller Agents via API",
                "Product search initiated",
              ],
            },
            detailedInfo: {
              title: "User Intent Processing",
              description:
                "The Buyer/Shopping Agent acts as the user's representative in the agentic commerce ecosystem.",
              mongodbOperations: [
                {
                  operation: "insertOne",
                  collection: "userIntents",
                  query:
                    '{ sessionId: "sess_123", intent: "browse_laptops", timestamp: ISODate() }',
                  result: "Intent logged for agent processing",
                },
                {
                  operation: "find",
                  collection: "sellerAgents",
                  query: '{ categories: "laptops", status: "active" }',
                  result: "3 active merchant agents found",
                },
              ],
              dataFlow: [
                "User expresses intent",
                "Buyer Agent captures request",
                "Seller Agent API queried",
                "Product options retrieved",
              ],
              actor: {
                name: "Buyer/Shopping Agent",
                role: "User's Representative",
                message:
                  "I received the user's intent to browse laptops. I will now query the Seller Agent through the merchant API to fetch available products from various merchants.",
              },
            },
          }
        }
        />
      )) : (
        <div style={{ padding: '20px', textAlign: 'center', opacity: 0.7 }}>
          No messages yet. Starting your shopping session...
        </div>
      )}
      
      {/* Show thinking message when agent is thinking */}
      {agentIsThinking && (
        <AgentThinking/>
      )}
      <div ref={messagesEndRef} />

    </div>
  );
};

export default ChatbotContainer;
