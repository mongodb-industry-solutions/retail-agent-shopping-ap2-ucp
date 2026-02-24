"use client";

import React, { useState } from 'react';
import { useDispatch } from 'react-redux';
import Button from "@leafygreen-ui/button";
import { H3 } from "@leafygreen-ui/typography";
import { palette } from "@leafygreen-ui/palette";
import { introSlides } from '@/lib/const/ux-writing';
import { setGuidedSlice } from '../../redux/slices/GlobalSlice';
import { Logo } from '@leafygreen-ui/logo';
import Icon from '@leafygreen-ui/icon';

const GuidedIntro = () => {
  const dispatch = useDispatch();
  const [currentSlide, setCurrentSlide] = useState(0);

  const slide = introSlides[currentSlide];
  const isLastSlide = currentSlide === introSlides.length - 1;

  const handleNext = () => {
    if (isLastSlide) {
      dispatch(setGuidedSlice(false));
    } else {
      setCurrentSlide((prev) => prev + 1);
    }
  };

  const handlePrevious = () => {
    if (currentSlide > 0) {
      setCurrentSlide((prev) => prev - 1);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center" style={{ backgroundColor: palette.gray.light3 }}>
      {/* Skip button */}
      <div className="absolute top-4 right-4 z-10">
        <Button
          variant="ghost"
          size="small"
          onClick={() => dispatch(setGuidedSlice(false))}
          className="flex items-center gap-2"
          aria-label="Skip introduction"
        >
          <span className="hidden sm:inline">Skip</span>
          <span className="h-5 w-5">✕</span>
        </Button>
      </div>

      {/* MongoDB Logo */}
      <div className="absolute top-6 left-6 flex items-center gap-2">
        <Logo height={30} color='green-dark-2' />
      </div>

      <div className="w-full max-w-4xl px-6">
        {/* Progress indicators */}
        <div className="flex justify-center gap-2 mb-12">
          {introSlides.map((_, index) => {
            let backgroundColor;
            if (index === currentSlide) {
              backgroundColor = palette.green.dark2;
            } else if (index < currentSlide) {
              backgroundColor = palette.green.dark1;
            } else {
              backgroundColor = palette.gray.light2;
            }
            
            return (
              <button
                key={index}
                onClick={() => setCurrentSlide(index)}
                className={`h-2 rounded-full transition-all duration-300 ${
                  index === currentSlide ? "w-10" : "w-6"
                }`}
                style={{ backgroundColor }}
                aria-label={`Go to slide ${index + 1}`}
              />
            );
          })}
        </div>

        {/* Slide content */}
        <div className="text-center space-y-8">
          {/* Image */}
          <div className="flex justify-center">
            <div className="w-full max-w-md aspect-video rounded-xl overflow-hidden">
              <img 
                src={slide.imageURL}
                alt={slide.imagePlaceholder}
                className="w-full h-full object-contain"
                style={{
                  border: `2px solid ${palette.gray.light1}`,
                  borderRadius: '12px'
                }}
              />
            </div>
          </div>

          <div className="space-y-4">
            <p className="text-sm font-semibold tracking-wide uppercase" style={{ color: palette.green.dark2 }}>
              {currentSlide + 1} / {introSlides.length}
            </p>
            <H3 className="text-balance" style={{ color: palette.gray.dark3 }}>
              {slide.title}
            </H3>
            <div 
              className="text-lg max-w-2xl mx-auto leading-relaxed"
              style={{ color: palette.gray.dark1 }}
              dangerouslySetInnerHTML={{ __html: slide.description }}
            />
          </div>
        </div>

        {/* Navigation */}
        <div className="flex justify-center items-center gap-4 mt-16">
          {currentSlide > 0 && (
            <Button
              variant="default"
              size="large"
              leftGlyph={<Icon glyph="CaretLeft" />}
              onClick={handlePrevious}
              style={{
                backgroundColor: palette.gray.light2,
                color: palette.gray.dark1,
                border: `1px solid ${palette.gray.light1}`
              }}
            >
              Previous
            </Button>
          )}
          <Button 
            size="large" 
            onClick={handleNext}
            rightGlyph={<Icon glyph="CaretRight" />}
            style={{
              backgroundColor: palette.green.dark2,
              color: palette.gray.light3
            }}
          >
            {isLastSlide ? "Start Demo" : "Continue"}
          </Button>
        </div>
      </div>
    </div>
  );
}

export default GuidedIntro;