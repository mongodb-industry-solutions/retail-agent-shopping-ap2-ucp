"use client";

import { journeys } from "@/lib/const/ux-writing";
import { Badge } from "@leafygreen-ui/badge";
import Button from "@leafygreen-ui/button";
import Icon from "@leafygreen-ui/icon";
import { Logo } from "@leafygreen-ui/logo";
import { palette } from "@leafygreen-ui/palette";
import { Body } from "@leafygreen-ui/typography";
import { useRouter } from "next/navigation";
import React from "react";
import { useSelector } from "react-redux";

const ShoppingAssistantNavbar = ({ journeyId }) => {
  const router = useRouter();
  const messages = useSelector((state) => state.Global.messages);

  return (
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
          onClick={() => router.push(`/`)}
          leftGlyph={<Icon size={"xlarge"} glyph="ChevronLeft" />}
        />
        <div>
          <h2 style={{ margin: 0 }}>Shopping Assistant</h2>
          <small
            className="d-flex flex-row flex-align-center gap-1"
            style={{ color: "#666" }}
          >
            Powered by <Logo height={20} color="green-dark-2" />
          </small>
        </div>
      </div>
      <div className="d-flex flex-column align-items-center">
        <div className="d-flex flex-row align-items-center gap-2">
          <Badge variant="blue" size="small">
            {journeys[journeyId]?.characteristic}
          </Badge>
          <Icon size={"small"} glyph="Cursor" />
          <Body
            onClick={() => console.log("GlobalSlice.messages:", messages)}
            style={{ fontSize: "14px" }}
          >
            Click any message to explore
          </Body>
        </div>
        <div>
          <Body
            style={{ fontSize: "14px" }}
          >
            Click any message to explore
          </Body>
        </div>
      </div>
    </div>
  );
};

export default ShoppingAssistantNavbar;
