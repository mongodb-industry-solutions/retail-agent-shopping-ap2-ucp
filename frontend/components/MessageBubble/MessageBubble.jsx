"use client";

import React from "react";
import { Chip } from "@leafygreen-ui/chip";
import Button from "@leafygreen-ui/button";
import { Body, Subtitle } from "@leafygreen-ui/typography";
import { palette } from "@leafygreen-ui/palette";
import Icon from "@leafygreen-ui/icon";
import { AGENT_ROLE, USER_ROLE } from "@/lib/constants/messages";

const MessageBubble = ({
  messageType,
  messageContent,
  messageOptions,
  onOptionClick,
  isLatest,
  messageDetails,
  setSelectedMessage,
}) => {
  const isUser = messageType === USER_ROLE;
  const isAgent = messageType === AGENT_ROLE;
  const hasDetails = !!messageDetails?.detailedInfo || !!messageDetails?.behindTheScenes;

  return (
    <>
      {/* Agent header - only show for agent messages */}
      {isAgent && (
        <div className="agentHeader">
          <img
            src="/icons/coachGTM_Headshot.png"
            className="agentImage"
            alt="Agent headshot"
          />
          <Subtitle className="agentPrefix">Agent's response</Subtitle>
        </div>
      )}

      {/* Message bubble with conditional styling */}
      <div
        className={`speechBubble d-flex flex-col ${isUser ? "userBubble" : "agentBubble"}`}
        style={isUser ? { backgroundColor: palette.green.dark2 } : {}}
      >
        <Body 
          style={isUser ? { color: "white" } : {}} 
          className={isUser ? "text-start messageContent" : "messageContent"}
        >
          {messageContent}
        </Body>

        {/* Message details section */}
        {hasDetails && (
          <>
            <hr className="m-0" />
            <div
              className="agentDetails"
              style={{ 
                backgroundColor: isUser ? palette.green.light3 : palette.gray.light3 
              }}
            >
              {/* Details header */}
              <div className="d-flex justify-content-between">
                <div className="d-flex flex-row align-items-center gap-2">
                  <Icon
                    style={{ color: palette.green.dark2 }}
                    glyph="Database"
                  />
                  <Subtitle
                    className="agentPrefix"
                    style={{ color: palette.green.dark2 }}
                  >
                    Behind The Scenes
                  </Subtitle>
                </div>
                <Button
                  rightGlyph={<Icon glyph="ArrowRight" />}
                  size="small"
                  variant="primaryOutlined"
                  onClick={() => setSelectedMessage(messageDetails)}
                >
                  Click for details
                </Button>
              </div>

              {/* Details content */}
              {(messageDetails?.behindTheScenes || messageDetails?.detailedInfo) && (
                <div>
                  <p className="behindTheScenesSummary m-0">
                    {messageDetails.behindTheScenes?.summary || ""}
                  </p>
                  {messageDetails.behindTheScenes?.keyPoints && (
                    <div className="mt-2 flex flex-wrap gap-1.5">
                      {messageDetails.behindTheScenes.keyPoints.map((point, i) => (
                        <Chip key={i} label={point} className="chip p-1" />
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          </>
        )}
      </div>

      {/* Message options - only show for latest message with options */}
      {isLatest && messageOptions && (
        <div className="d-flex flex-row flex-wrap gap-3">
          {messageOptions.map((option) => (
            <Button
              key={option.id}
              leftGlyph={<Icon glyph="Sparkle" />}
              size="small"
              variant="default"
              onClick={() =>
                onOptionClick(option.id, option.nextMessageId, option.text)
              }
            >
              {option.text}
            </Button>
          ))}
        </div>
      )}
    </>
  );
};

export default MessageBubble;
