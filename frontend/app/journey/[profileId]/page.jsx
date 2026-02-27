"use client";

import React, { useEffect, useState, useRef } from "react";
import { useRouter } from "next/navigation";
import { useParams } from "next/navigation";
import { useDispatch } from "react-redux";
import Button from "@leafygreen-ui/button";
import { Body, Subtitle } from "@leafygreen-ui/typography";
import Icon from "@leafygreen-ui/icon";
import { palette } from "@leafygreen-ui/palette";
import Badge from "@leafygreen-ui/badge";

import "../journey.css";
import { profiles, chatFlows } from "@/lib/const/ux-writing";
import { addStartedJourney } from "@/redux/slices/GlobalSlice";
import { Chip } from "@leafygreen-ui/chip";
import { Logo } from "@leafygreen-ui/logo";

export default function JourneyPage() {
  const router = useRouter();
  const params = useParams();
  const { profileId } = params;
  const profile = profiles[profileId];
  const dispatch = useDispatch();
  const [messages, setMessages] = useState([]);
  const [selectedMessage, setSelectedMessage] = useState(null);
  const [sidebarWidth, setSidebarWidth] = useState(420);
  const [isResizing, setIsResizing] = useState(false);
  const messagesEndRef = useRef(null);

  const flow = chatFlows[profileId] || chatFlows.straightforward;

  useEffect(() => {
    dispatch(addStartedJourney(profileId));
  }, []);

  useEffect(() => {
    const firstMessage = flow.find((m) => m.id === "welcome");
    if (firstMessage) {
      setMessages([{ ...firstMessage, timestamp: new Date() }]);
    }
  }, [profileId, flow]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

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

  const handleMouseDown = () => {
    setIsResizing(true);
  };

  useEffect(() => {
    const handleMouseMove = (e) => {
      if (!isResizing) return;
      const newWidth = window.innerWidth - e.clientX;
      const maxWidth = Math.floor(window.innerWidth / 2);
      setSidebarWidth(Math.min(Math.max(320, newWidth), maxWidth));
    };

    const handleMouseUp = () => {
      setIsResizing(false);
    };

    if (isResizing) {
      document.addEventListener("mousemove", handleMouseMove);
      document.addEventListener("mouseup", handleMouseUp);
    }

    return () => {
      document.removeEventListener("mousemove", handleMouseMove);
      document.removeEventListener("mouseup", handleMouseUp);
    };
  }, [isResizing]);

  if (!profile) {
    return <div>Shopping journey not found.</div>;
  }

  return (
    <div
      className="JourneyPage"
      style={{ height: "100vh", display: "flex", overflow: "hidden" }}
    >
      {/* Main Chat */}
      <div style={{ flex: 1, display: "flex", flexDirection: "column" }}>
        {/* Header */}
        <div
          style={{
            padding: "16px 24px",
            borderBottom: `1px solid ${palette.gray.light2}`,
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <Button
              variant="ghost"
              size=""
              onClick={() => router.push(`/`)}
              leftGlyph={<Icon size={"xlarge"} glyph="ChevronLeft" />}
            />
            <div>
              <h2 style={{ margin: 0 }}>Shopping Assistant</h2>
              <small className="d-flex flex-row flex-align-center gap-1" style={{ color: "#666" }}>
                Powered by <Logo height={20} color='green-dark-2' />
              </small>
            </div>
          </div>
          <div className="d-flex flex-row align-items-center gap-2">
            <Icon size={"small"} glyph="Cursor" />
            <Body style={{fontSize: "14px"}}>Click any message to explore</Body>
            <Badge variant="blue" size="small">{profiles[profileId].characteristic}</Badge>
          </div>
        </div>

        {/* Messages */}
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
      </div>

      {/* Sidebar */}
      {selectedMessage && (
        <>
          <div
            style={{
              width: 4,
              cursor: "col-resize",
              background: "#e0e0e0",
            }}
            onMouseDown={handleMouseDown}
          />

          <div
            style={{
              width: sidebarWidth,
              borderLeft: "1px solid #e0e0e0",
              padding: 24,
              overflowY: "auto",
            }}
          >
            <h3>{selectedMessage.detailedInfo?.title}</h3>
            <p>{selectedMessage.detailedInfo?.description}</p>
          </div>
        </>
      )}
    </div>
  );
}

function MessageBubble({
  messageType,
  messageContent,
  messageOptions,
  onOptionClick,
  isLatest,
  message,
}) {
  if (messageType === "user") {
    return (
      <div
        className="speechBubble userBubble d-flex flex-col"
         style={{ backgroundColor: palette.green.dark2 }}
      >
        <Body style={{color: "white"}} className="text-start messageContent">{messageContent}</Body>
        <>
          <hr className="m-0" />
          <div
            className="agentDetails"
            style={{ backgroundColor: palette.green.light3 }}
          >
            {/* Agent header for details message */}
            <div className="d-flex justify-content-between">
              <div className="d-flex flex-row align-items-center gap-2">
                <Icon
                  style={{ color: palette.green.dark2 }}
                  glyph="Database"
                ></Icon>
                <Subtitle
                  className={"agentPrefix"}
                  style={{ color: palette.green.dark2 }}
                >
                  Behind The Scenes
                </Subtitle>
              </div>
              <Button
                rightGlyph={<Icon glyph="ArrowRight" />}
                size="small"
                variant="primaryOutlined"
              >
                Click for details
              </Button>
            </div>
            {/* Agent content for details message */}
            <div>
              <p className="behindTheScenesSummary m-0">
                {message.behindTheScenes.summary}
              </p>
              <div className="mt-2 flex flex-wrap gap-1.5">
                {message.behindTheScenes.keyPoints.map((point, i) => (
                  <Chip key={i} label={point} className="chip p-1" />
                ))}
              </div>
            </div>
          </div>
        </>
      </div>
    );
  }
  const hasDetails = !!message.detailedInfo;
  return (
    <>
      <div className="agentHeader">
        <img src="/icons/coachGTM_Headshot.png" className="agentImage" />
        <Subtitle className="agentPrefix">Agent's response</Subtitle>
      </div>
      <div className="speechBubble answerBubble">
        <Body className="messageContent">{messageContent}</Body>
        {/* Message details */}
        {hasDetails && (
          <>
            <hr className="m-0" />
            <div
              className="agentDetails"
              style={{ backgroundColor: palette.gray.light3 }}
            >
              {/* Agent header for details message */}
              <div className="d-flex justify-content-between">
                <div className="d-flex flex-row align-items-center gap-2">
                  <Icon
                    style={{ color: palette.green.dark2 }}
                    glyph="Database"
                  ></Icon>
                  <Subtitle
                    className={"agentPrefix"}
                    style={{ color: palette.green.dark2 }}
                  >
                    Behind The Scenes
                  </Subtitle>
                </div>
                <Button
                  rightGlyph={<Icon glyph="ArrowRight" />}
                  size="small"
                  variant="primaryOutlined"
                >
                  Click for details
                </Button>
              </div>
              {/* Agent content for details message */}
              <div>
                <p className="behindTheScenesSummary m-0">
                  {message.behindTheScenes.summary}
                </p>
                <div className="mt-2 flex flex-wrap gap-1.5">
                  {message.behindTheScenes.keyPoints.map((point, i) => (
                    <Chip key={i} label={point} className="chip p-1" />
                  ))}
                </div>
              </div>
            </div>
          </>
        )}
      </div>

      {isLatest && messageOptions && (
        <div className="d-flex flex-row flex-wrap gap-3">
          {messageOptions.map((option) => (
            <Button
              key={option.id}
              leftGlyph={<Icon glyph="Sparkle" />}
              size="small"
              variant="default"
               onClick={() => onOptionClick(option.id, option.nextMessageId, option.label) }
            >
              {option.label}
            </Button>
          ))}
        </div>
      )}
    </>
  );
}
