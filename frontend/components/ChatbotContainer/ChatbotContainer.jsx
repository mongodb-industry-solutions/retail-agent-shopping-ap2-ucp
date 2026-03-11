import React, { useEffect, useState, useRef } from "react";

import MessageBubble from "../MessageBubble/MessageBubble";

const ChatbotContainer = ({messages,setMessages }) => {
      const messagesEndRef = useRef(null);

  const handleOptionClick = (optionId, nextMessageId, optionLabel) => {
    const nextMessage = flow.find((m) => m.id === nextMessageId);

    const userMessage = {
      id: `user-${Date.now()}`,
      type: "user",
      content: optionLabel,
      timestamp: new Date(),
    };

    if (nextMessage) {
      setMessages((prev) => [
        ...prev,
        userMessage,
        { ...nextMessage, timestamp: new Date() },
      ]);
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
      {messages.map((message, index) => (
        <MessageBubble
          setSelectedMessage={setSelectedMessage}
          key={`${message.id}-${index}`}
          messageType={message.type}
          messageContent={message.content}
          messageOptions={message.options}
          onOptionClick={handleOptionClick}
          isLatest={index === messages.length - 1}
          message={{
            behindTheScenes: {
              summary: "Buyer/Shopping Agent received user intent",
              keyPoints: [
                "User intent captured",
                "Querying Seller Agents via API",
                "Product search initiated",
              ],
              // actor: {
              //   name: "Buyer/Shopping Agent",
              //   message:
              //     "I received the user's intent to browse laptops. I will now query the Seller Agent through the merchant API to fetch available products.",
              // },
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
          }}
        />
      ))}
      <div ref={messagesEndRef} />
    </div>
  );
};

export default ChatbotContainer;
