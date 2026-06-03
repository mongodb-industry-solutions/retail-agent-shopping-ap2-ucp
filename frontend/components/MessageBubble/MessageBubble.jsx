"use client";

import React from "react";
import { Chip } from "@leafygreen-ui/chip";
import Button from "@leafygreen-ui/button";
import { Body, Subtitle } from "@leafygreen-ui/typography";
import { palette } from "@leafygreen-ui/palette";
import Icon from "@leafygreen-ui/icon";
import { useDispatch, useSelector } from "react-redux";
import { AGENT_ROLE, SYSTEM_ROLE, USER_ROLE } from "@/lib/const/bubbleDetails";
import { setSelectedMessage } from "@/redux/slices/GlobalSlice";
import Image from "next/image";

/**
 * Parse inline formatting like **bold** and *italic*
 */
const parseInlineFormatting = (text) => {
  const elements = [];
  let currentIndex = 0;

  // Pattern to match **bold** and *italic* text
  const formatRegex = /(\*\*([^*]+)\*\*|\*([^*]+)\*)/g;
  let match;

  while ((match = formatRegex.exec(text)) !== null) {
    // Add text before the match
    if (match.index > currentIndex) {
      elements.push(text.substring(currentIndex, match.index));
    }

    // Add formatted text
    if (match[1].startsWith('**')) {
      // Bold text (**text**)
      elements.push(
        <strong key={`bold-${match.index}`} style={{ fontWeight: 'bold' }}>
          {match[2]}
        </strong>
      );
    } else {
      // Italic/emphasis text (*text*)
      elements.push(
        <em key={`italic-${match.index}`} style={{ fontStyle: 'italic', fontWeight: 'bold' }}>
          {match[3]}
        </em>
      );
    }

    currentIndex = match.index + match[1].length;
  }

  // Add remaining text
  if (currentIndex < text.length) {
    elements.push(text.substring(currentIndex));
  }

  return elements.length > 0 ? elements : text;
};

/**
 * Parse markdown-like text content and return JSX elements
 * Handles: **bold**, *italic*, ### headings, bullet points, line breaks
 */
const parseMarkdownContent = (text) => {
  if (!text) return '';

  const lines = text.split('\n');
  const elements = [];

  lines.forEach((line, lineIndex) => {
    // Skip empty lines but preserve spacing
    if (line.trim() === '') {
      elements.push(<br key={`br-${lineIndex}`} />);
      return;
    }

    // Handle headings (### **text** or ### text)
    if (line.trim().startsWith('### ')) {
      const headingText = line.replace(/^### \*\*(.*)\*\*$/, '$1').replace(/^### (.*)$/, '$1');
      elements.push(
        <span key={`heading-${lineIndex}`} style={{ 
          display: 'block',
          fontWeight: 'bold', 
          fontSize: '18px', 
          margin: '16px 0 8px 0',
          color: '#1e3a8a'
        }}>
          {headingText}
        </span>
      );
      return;
    }

    // Handle bullet points (*   text)
    if (line.trim().startsWith('*   ')) {
      const bulletText = line.replace(/^\*\s+/, '');
      const parsedBulletText = parseInlineFormatting(bulletText);
      elements.push(
        <span key={`bullet-${lineIndex}`} style={{ 
          display: 'block',
          marginLeft: '20px', 
          marginBottom: '4px',
          position: 'relative'
        }}>
          <span style={{ 
            position: 'absolute', 
            left: '-15px', 
            top: '0px' 
          }}>•</span>
          {parsedBulletText}
        </span>
      );
      return;
    }

    // Handle regular paragraphs with inline formatting
    const parsedLine = parseInlineFormatting(line);
    elements.push(
      <span key={`line-${lineIndex}`} style={{ display: 'block', marginBottom: '8px' }}>
        {parsedLine}
      </span>
    );
  });

  return elements;
};

const MessageBubble = ({message, isLatest, onOptionClick, hasBehindTheScenes}) => {
  const {
    id: messageId,
    type: messageType,
    content: messageContent,
    messageOptions,
    bubbleDetails = null,
  } = message;
  const dispatch = useDispatch();
  const isUser = messageType === USER_ROLE;
  const isAgent = messageType === AGENT_ROLE;
  const selectedMessage = useSelector((state) => state.Global.selectedMessage);
  const isSelectedMessage = selectedMessage?.id === messageId;  

  if(messageType === SYSTEM_ROLE)
    return
  return (
    <>
      {/* Agent header - only show for agent messages */}
      {isAgent && (
        <div className="agentHeader">
          <Image
            src="/icons/ShoppingAgentAP2chatFlow.png"
            alt="Agent headshot"
            width={60}
            height={60}
          />
          <Subtitle className="agentPrefix">Agent's response</Subtitle>
        </div>
      )}
      {/* Message bubble with conditional styling */}
      <div
        className={`speechBubble d-flex flex-col ${isUser ? "userBubble" : "agentBubble"}`}
        style={{
          ...(isUser ? { backgroundColor: palette.green.dark2 } : {}),
          ...(isSelectedMessage == true ? { 
            border: `3px solid #00ff00`,
            boxShadow: `0 0 12px rgba(0, 255, 0, 0.5)`,
            transform: 'scale(1.02)'
          } : {})
        }}
      >
        <Body
          style={isUser ? { color: "white" } : {}}
          className={isUser ? "text-start messageContent" : "messageContent"}
        >
          {isUser ? messageContent : parseMarkdownContent(messageContent)}
        </Body>
        {/* Message details section */}
        {hasBehindTheScenes  && (
          <>
            <hr className="m-0" />
          <div
            className="agentDetails"
            style={{
              backgroundColor: isUser
                ? palette.green.light3
                : palette.gray.light3,
            }}
          >
            {/* Details header */}
            {hasBehindTheScenes && (
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
                  onClick={() => dispatch(setSelectedMessage(message))}
                >
                  Click for details
                </Button>
              </div>
            )}

            {/* Details content */}
            {bubbleDetails && (
              <div>
                <p className="behindTheScenesSummary m-0">
                  {bubbleDetails.text || ""}
                </p>
                {bubbleDetails.tags && (
                  <div className="mt-2 flex flex-wrap gap-1.5">
                    {bubbleDetails.tags.map((tag, i) => (
                      <Chip key={i} label={tag} className="chip p-1" />
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
          {messageOptions.map((option, index) => (
            <Button
              key={`option-${index}`}
              leftGlyph={<Icon glyph="Sparkle" />}
              size="small"
              variant="default"
              style={{height: 'fit-content'}}
              onClick={() =>
                onOptionClick( option)
              }
            >
              {option}
            </Button>
          ))}
        </div>
      )}
    </>
  );
};

export default MessageBubble;
