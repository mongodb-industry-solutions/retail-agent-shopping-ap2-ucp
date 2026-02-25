"use client";

import React, { useState } from 'react';
import { useDispatch } from 'react-redux';
import Button from "@leafygreen-ui/button";
import Card from "@leafygreen-ui/card";
import Badge from "@leafygreen-ui/badge";
import Icon from "@leafygreen-ui/icon";
import IconButton from "@leafygreen-ui/icon-button";
import Tooltip from "@leafygreen-ui/tooltip";
import { H3, Body, H2, H1 } from "@leafygreen-ui/typography";
import { palette } from "@leafygreen-ui/palette";
import { spacing } from "@leafygreen-ui/tokens";
import { profiles } from '@/lib/const/ux-writing';
import { setGuidedSlice } from '../../redux/slices/GlobalSlice';

const profileIcons = {
  straightforward: "Checkmark",
  hunter: "CreditCard", 
  disputing: "Warning",
};

const profileOrder = ["straightforward", "hunter", "disputing"];

const ProfileSelection = ({ onSelectProfile, startedJourneys = [] }) => {
  const dispatch = useDispatch();
  const [hoveredProfile, setHoveredProfile] = useState(null);
  const [showTooltip, setShowTooltip] = useState(null);
  const completedJourneys = startedJourneys;

  const handleOpenIntro = () => {
    dispatch(setGuidedSlice(true));
  };

  const isUnlocked = (profileId) => {
    const profileIndex = profileOrder.indexOf(profileId);
    if (profileIndex === 0) return true;
    const previousJourney = profileOrder[profileIndex - 1];
    return startedJourneys.includes(previousJourney);
  };

  const isStarted = (profileId) => {
    return startedJourneys.includes(profileId);
  };

  const getPreviousJourneyName = (profileId) => {
    const profileIndex = profileOrder.indexOf(profileId);
    if (profileIndex <= 0) return "";
    const previousJourney = profileOrder[profileIndex - 1];
    const profile = profiles.find((p) => p.id === previousJourney);
    return profile?.name || "";
  };

  const isCompleted = (profileId) => {
    return completedJourneys.includes(profileId);
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center" style={{ 
      padding: spacing[3]
    }}>
      <div className="w-full max-w-5xl" style={{ 
        display: 'flex', 
        flexDirection: 'column', 
        justifyContent: 'space-around',
        minHeight: '100vh'
      }}>
        {/* Header */}
        <header className="text-center" style={{ 
          display: 'flex', 
          flexDirection: 'column', 
          gap: spacing[3],
          marginTop: '-50px'

        }}>
          <H1 className="tracking-tight" style={{ color: palette.gray.dark3 }}>
            Interactive Agentic Commerce Demo
          </H1>
          <div className="flex items-center justify-center" style={{ gap: spacing[4] }}>
            {/* AP2 Icon */}
            <div className="flex items-center" style={{ gap: spacing[2] }}>
              <div 
                className="h-10 w-10 rounded-lg flex items-center justify-center"
                style={{ backgroundColor: palette.blue.base }}
              >
                <span className="text-xs font-bold text-white">AP2</span>
              </div>
              <Body size="small" style={{ color: palette.gray.dark1}}>Agent Protocol</Body>
            </div>
            {/* MongoDB Icon */}
            <div className="flex items-center" style={{ gap: spacing[2] }}>
              <div 
                className="h-10 w-10 rounded-lg flex items-center justify-center"
                style={{ backgroundColor: palette.green.dark2 }}
              >
                <span className="text-xs font-bold text-white">M</span>
              </div>
              <Body size="small" style={{ color: palette.gray.dark}}>MongoDB</Body>
            </div>
          </div>
          <Body className="w-full mx-auto" style={{ 
            color: palette.gray.dark1, 
            textAlign: 'center', 
            fontSize: '18px',
            lineHeight: '1.5'
          }}>
            Navigate through three progressive shopping scenarios to discover how
            MongoDB powers real-time payment decisions in AP2/UCP protocols.
          </Body>
        </header>

        {/* Profile Cards */}
        <div className="grid md:grid-cols-3" style={{ gap: spacing[3] }}>
          {profiles.map((profile, index) => {
            const iconGlyph = profileIcons[profile.id];
            const isHovered = hoveredProfile === profile.id;
            const unlocked = isUnlocked(profile.id);
            const started = isStarted(profile.id);
            const previousJourney = getPreviousJourneyName(profile.id);

            // Profile-specific colors
            const getProfileColors = () => {
              switch (profile.id) {
                case 'straightforward':
                  return {
                    bg: palette.green.light3,
                    border: isHovered ? palette.green.dark2 : palette.green.light2,
                    icon: palette.green.dark2,
                    badge: 'green',
                    button: { bg: palette.green.dark2, text: 'white' }
                  };
                case 'hunter':
                  return {
                    bg: palette.blue.light2,
                    border: isHovered ? palette.blue.base : palette.blue.light1,
                    icon: palette.blue.base,
                    badge: 'blue',
                    button: { bg: palette.blue.base, text: 'white' }
                  };
                case 'disputing':
                  return {
                    bg: palette.yellow.light2,
                    border: isHovered ? palette.yellow.base : palette.yellow.light1,
                    icon: palette.yellow.dark2,
                    badge: 'yellow',
                    button: { bg: palette.yellow.base, text: palette.gray.dark2 }
                  };
                default:
                  return {
                    bg: palette.gray.light2,
                    border: palette.gray.light1,
                    icon: palette.gray.base,
                    badge: 'lightgray',
                    button: { bg: palette.gray.light2, text: palette.gray.base }
                  };
              }
            };

            const profileColors = getProfileColors();

            return (
              <Card
                key={profile.id}
                style={{
                  padding: spacing[3],
                  transform: isHovered && unlocked ? 'scale(1.02)' : 'scale(1)',
                  transition: 'all 0.3s ease',
                  opacity: unlocked ? 1 : 0.6,
                  cursor: unlocked ? 'pointer' : 'not-allowed',
                  border: `2px solid ${unlocked ? profileColors.border : palette.gray.light2}`,
                  position: 'relative'
                }}
                onMouseEnter={() => unlocked && setHoveredProfile(profile.id)}
                onMouseLeave={() => setHoveredProfile(null)}
                onClick={() => unlocked && onSelectProfile && onSelectProfile(profile.id)}
              >
                {/* Step Number */}
                <div className="absolute" style={{ top: spacing[2], left: spacing[2] }}>
                  <div
                    className="h-7 w-7 rounded-full flex items-center justify-center text-sm font-bold"
                    style={{
                      backgroundColor: unlocked ? palette.gray.light2 : palette.gray.light3,
                      color: unlocked ? palette.gray.dark2 : palette.gray.base
                    }}
                  >
                    {index + 1}
                  </div>
                </div>

                {/* Info Icon with Tooltip */}
                <div className="absolute" style={{ top: spacing[2], right: spacing[2] }}>
                  <Tooltip
                    trigger={
                      <IconButton aria-label="Profile information">
                        <Icon glyph="InfoWithCircle" />
                      </IconButton>
                    }
                    triggerEvent="hover"
                    placement="bottom"
                  >
                    <div style={{ maxWidth: '300px', padding: spacing[2] }}>
                      <div className="flex items-center" style={{ gap: spacing[1], marginBottom: spacing[2] }}>
                        <Icon glyph="InfoWithCircle" fill={palette.green.dark2} />
                        <Body weight="medium">About this journey</Body>
                      </div>
                      <Body size="small">{profile.detailedInfo}</Body>
                      {!unlocked && (
                        <div className="flex items-center" style={{ 
                          gap: spacing[1], 
                          marginTop: spacing[2], 
                          paddingTop: spacing[2], 
                          borderTop: `1px solid ${palette.gray.light1}` 
                        }}>
                          <Icon glyph="Lock" fill={palette.gray.base} />
                          <Body size="small" style={{ color: palette.gray.dark1 }}>Start "{previousJourney}" to unlock</Body>
                        </div>
                      )}
                    </div>
                  </Tooltip>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: spacing[3], marginTop: spacing[2] }}>
                  {/* Icon */}
                  <div className="flex justify-center">
                    <div
                      className="p-4 rounded-2xl"
                      style={{
                        backgroundColor: unlocked ? profileColors.bg : palette.gray.light2
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
                  <div className="text-center" style={{ display: 'flex', flexDirection: 'column', gap: spacing[2] }}>
                    <H3 style={{ color: palette.gray.dark2 }}>
                      {profile.name}
                    </H3>
                    <div className="flex justify-center">
                      <Badge 
                        variant={unlocked ? profileColors.badge : 'lightgray'}
                      >
                        {profile.characteristic}
                      </Badge>
                    </div>
                    <p className="leading-relaxed" style={{ color: palette.gray.dark1, fontSize: '14px' }}>
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
                        width: '100%'
                      }}
                      onClick={() => onSelectProfile && onSelectProfile(profile.id)}
                    >
                      {started ? "Continue Journey" : "Start Journey"}
                    </Button>
                  ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: spacing[1] }}>
                      <Button
                        disabled
                        leftGlyph={<Icon glyph="Lock" />}
                        style={{ width: '100%' }}
                      >
                        Locked
                      </Button>
                      <Body size="small" className="text-center" style={{ color: palette.gray.dark1 }}>
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
        <div className="flex justify-center">
          <Button
            variant="outline"
            leftGlyph={<Icon glyph="University" />}
            onClick={handleOpenIntro}
          >
            View Introduction Guide
          </Button>
        </div>
      </div>
    </div>
  );
};

export default ProfileSelection;