import React from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { setGuidedSlice } from '../../redux/slices/GlobalSlice';
import GuidedIntro from './GuidedIntro';

const GuidedIntroManager = () => {
  const isGuidedIntroOpened = useSelector(state => state.Global.isGuidedSliceOpened);
  const dispatch = useDispatch();

  const handleClose = () => {
    dispatch(setGuidedSlice(false));
  };

  return isGuidedIntroOpened ? <GuidedIntro onClose={handleClose} /> : null;
}

export default GuidedIntroManager