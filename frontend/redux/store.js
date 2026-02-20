import { configureStore } from '@reduxjs/toolkit';
import MandateLedgerReducer from './slices/MandateLedgerSlice'


const store = configureStore({
    reducer: {
        "MandateLedger": MandateLedgerReducer
    }
});

export default store;
