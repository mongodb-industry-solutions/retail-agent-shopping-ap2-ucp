"use client";

import React, { useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useRouter } from "next/navigation";
import Button from "@leafygreen-ui/button";
import { Card } from "@leafygreen-ui/card";
import Badge from "@leafygreen-ui/badge";
import Icon from "@leafygreen-ui/icon";
import IconButton from "@leafygreen-ui/icon-button";
import Tooltip from "@leafygreen-ui/tooltip";
import { H3, Body, H1 } from "@leafygreen-ui/typography";
import { palette } from "@leafygreen-ui/palette";
import { spacing } from "@leafygreen-ui/tokens";
import { journeys } from "@/lib/const/ux-writing";
import { setGuidedSlice } from "../../redux/slices/GlobalSlice";
import OrderSelectionModal from "../OrderSelectionModal/OrderSelectionModal";

const profileOrder = ["straightforward", "hunter", "disputing"];

const ProfileSelection = () => {
  const router = useRouter();
  const dispatch = useDispatch();
  const startedJourneys = useSelector((state) => state.Global.startedJourneys);
  const [hoveredProfile, setHoveredProfile] = useState(null);
  const [showOrderSelectionModal, setShowOrderSelectionModal] = useState(false);

  const onSelectProfile = (profileId) => {
    if (profileId === journeys.disputing.id && !startedJourneys.includes(journeys.disputing.id)) {
      setShowOrderSelectionModal(true);
    } else {
      router.push(`/journey/${profileId}`);
    }
  };

  const handleCloseModal = () => {
    setShowOrderSelectionModal(false);
  };

  const redirectToStartDisputingJourney = () => {
    // Logic for order selection will be implemented later
    setShowOrderSelectionModal(false);
    router.push(`/journey/disputing`);
  };

  const handleOpenIntro = () => {
    dispatch(setGuidedSlice(true));
  };

  const isUnlocked = (profileId) => {
    // Straightforward is always unlocked initially
    if (profileId === 'straightforward') return true;
    
    // Hunter and disputing are unlocked when straightforward is started
    if (profileId === 'hunter' || profileId === 'disputing') {
      return startedJourneys.includes('straightforward');
    }
    
    return false;
  };

  const isStarted = (profileId) => {
    return startedJourneys.includes(profileId);
  };

  const getPreviousJourneyName = (profileId) => {
    // For hunter and disputing, they need the straightforward journey to be started
    if (profileId === 'hunter' || profileId === 'disputing') {
      return journeys.straightforward?.name || "";
    }
    return "";
  };

  return (
    <div
      className="container d-flex flex-column justify-content-between"
      style={{ minHeight: "100vh" }}
    >
      {/* Header */}
      <header
        className="text-center mt-5 pt-5"
        style={{
          display: "flex",
          flexDirection: "column",
          gap: spacing[5],
        }}
      >
        <H1> Interactive Agentic Commerce Demo </H1>
        <Body
          className="w-full mx-auto pb-4"
          style={{
            color: palette.gray.dark1,
            textAlign: "center",
            fontSize: "20px",
            lineHeight: "1.5",
          }}
        >
          Navigate through three progressive shopping scenarios to discover how
          MongoDB powers real-time payment decisions in AP2/UCP protocols.
        </Body>
      </header>

      {/* Profile Cards */}
      <div className="grid md:grid-cols-3" style={{ gap: spacing[3] }}>
        {profileOrder.map((profileId, index) => {
          const profile = journeys[profileId];
          const iconGlyph = profile?.profileIcon || "User";
          const isHovered = hoveredProfile === profile.id;
          const unlocked = isUnlocked(profile.id);
          const started = isStarted(profile.id);
          const previousJourney = getPreviousJourneyName(profile.id);

          // Profile-specific colors
          const getProfileColors = () => {
            switch (profile.id) {
              case "straightforward":
                return {
                  bg: palette.green.light3,
                  border: isHovered
                    ? palette.green.dark2
                    : palette.green.light2,
                  icon: palette.green.dark2,
                  badge: "green",
                  button: { bg: palette.green.dark2, text: "white" },
                };
              case "hunter":
                return {
                  bg: palette.blue.light2,
                  border: isHovered ? palette.blue.base : palette.blue.light1,
                  icon: palette.blue.base,
                  badge: "blue",
                  button: { bg: palette.blue.base, text: "white" },
                };
              case "disputing":
                return {
                  bg: palette.yellow.light2,
                  border: isHovered
                    ? palette.yellow.base
                    : palette.yellow.light1,
                  icon: palette.yellow.dark2,
                  badge: "yellow",
                  button: { bg: palette.yellow.base, text: palette.gray.dark2 },
                };
              default:
                return {
                  bg: palette.gray.light2,
                  border: palette.gray.light1,
                  icon: palette.gray.base,
                  badge: "lightgray",
                  button: { bg: palette.gray.light2, text: palette.gray.base },
                };
            }
          };

          const profileColors = getProfileColors();

          return (
            <Card
              key={profile.id}
              onMouseEnter={() => unlocked && setHoveredProfile(profile.id)}
              onMouseLeave={() => setHoveredProfile(null)}
              onClick={() => unlocked && onSelectProfile(profile.id)}
            >
              {/* Step Number */}
              <div
                className="absolute"
                style={{ top: spacing[2], left: spacing[2] }}
              >
                <div
                  className="h-7 w-7 rounded-full flex items-center justify-center text-sm font-bold"
                  style={{
                    backgroundColor: unlocked
                      ? palette.gray.light2
                      : palette.gray.light3,
                    color: unlocked ? palette.gray.dark2 : palette.gray.base,
                  }}
                >
                  {index + 1}
                </div>
              </div>

              {/* Info Icon with Tooltip */}
              <div
                className="absolute"
                style={{ top: spacing[2], right: spacing[2] }}
              >
                <Tooltip
                  trigger={
                    <IconButton aria-label="Profile information">
                      <Icon glyph="InfoWithCircle" />
                    </IconButton>
                  }
                  triggerEvent="hover"
                  placement="bottom"
                >
                  <div style={{ maxWidth: "300px", padding: spacing[2] }}>
                    <div
                      className="flex items-center"
                      style={{ gap: spacing[1], marginBottom: spacing[2] }}
                    >
                      <Icon glyph="InfoWithCircle" fill={palette.green.dark2} />
                      <Body weight="medium">About this journey</Body>
                    </div>
                    <Body size="small" className="text-start">
                      {profile.detailedInfo}
                    </Body>
                    {!unlocked && (
                      <div
                        className="flex items-center"
                        style={{
                          gap: spacing[1],
                          marginTop: spacing[2],
                          paddingTop: spacing[2],
                          borderTop: `1px solid ${palette.gray.light1}`,
                        }}
                      >
                        <Icon glyph="Lock" fill={palette.gray.base} />
                        <Body
                          size="small"
                          className="text-start"
                          style={{ color: palette.gray.dark1 }}
                        >
                          Start "{previousJourney}" to unlock
                        </Body>
                      </div>
                    )}
                  </div>
                </Tooltip>
              </div>

              <div
                style={{
                  display: "flex",
                  flexDirection: "column",
                  gap: spacing[3],
                  marginTop: spacing[2],
                }}
              >
                {/* Icon */}
                <div className="flex justify-center">
                  <div
                    className="p-4 rounded-2xl"
                    style={{
                      backgroundColor: unlocked
                        ? profileColors.bg
                        : palette.gray.light2,
                    }}
                  >
                    <Icon
                      glyph={iconGlyph}
                      size="xlarge"
                      fill={unlocked ? profileColors.icon : palette.gray.base}
                    />
                  </div>
                </div>

                {/* Content */}
                <div
                  className="text-center"
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    gap: spacing[2],
                  }}
                >
                  <H3 style={{ color: palette.gray.dark2 }}>{profile.name}</H3>
                  <div className="flex justify-center">
                    <Badge
                      variant={unlocked ? profileColors.badge : "lightgray"}
                    >
                      {profile.characteristic}
                    </Badge>
                  </div>
                  <p
                    className="leading-relaxed mt-3"
                    style={{ color: palette.gray.dark1, fontSize: "16px" }}
                  >
                    {profile.description}
                  </p>
                </div>

                {/* Select Button */}
                {unlocked ? (
                  <Button
                    variant="primary"
                    size="large"
                    rightGlyph={<Icon glyph="ArrowRight" />}
                    style={{
                      backgroundColor: profileColors.button.bg,
                      color: profileColors.button.text,
                      width: "100%",
                    }}
                    onClick={() => onSelectProfile(profile.id)}
                  >
                    {started ? "Continue Journey" : "Start Journey"}
                  </Button>
                ) : (
                  <div
                    style={{
                      display: "flex",
                      flexDirection: "column",
                      gap: spacing[1],
                    }}
                  >
                    <Button
                      disabled
                      leftGlyph={<Icon glyph="Lock" />}
                      style={{ width: "100%" }}
                    >
                      Locked
                    </Button>
                    <Body
                      className="text-center mt-1"
                      style={{ color: palette.gray.dark1, fontSize: "14px" }}
                    >
                      Start "{previousJourney}" first
                    </Body>
                  </div>
                )}
              </div>
            </Card>
          );
        })}
      </div>

      {/* Reopen Intro Button */}
      <div className="flex justify-center mb-4 pt-4">
        <Button
          variant=""
          leftGlyph={<Icon glyph="University" />}
          onClick={handleOpenIntro}
        >
          View Introduction Guide
        </Button>
      </div>

      {/* Order Selection Modal for Disputing Journey */}
      <OrderSelectionModal
        show={showOrderSelectionModal}
        onHide={handleCloseModal}
        redirectToStartDisputingJourney={redirectToStartDisputingJourney}
      />
    </div>
  );
};

export default ProfileSelection;
