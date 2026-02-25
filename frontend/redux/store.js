import { configureStore } from '@reduxjs/toolkit';
import MandateLedgerReducer from './slices/MandateLedgerSlice'
import GlobalSliceReducer from './slices/GlobalSlice'


const store = configureStore({
    reducer: {
        "MandateLedger": MandateLedgerReducer,
        "Global": GlobalSliceReducer
    }
});

export default store;
