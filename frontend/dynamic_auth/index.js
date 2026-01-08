/**
 * Dynamic Wallet Authentication Module for OpenCEX Frontend
 *
 * This module provides wallet-based authentication using Dynamic XYZ SDK.
 *
 * Setup Instructions:
 * 1. Install dependencies: npm install @dynamic-labs/sdk-react-core @dynamic-labs/ethereum
 * 2. Import components in your main.ts/main.js
 * 3. Register the wallet store module
 * 4. Wrap your app with DynamicProvider
 * 5. Replace login route with DynamicLogin component
 */

import DynamicProvider from './DynamicProvider.vue';
import DynamicLogin from './DynamicLogin.vue';
import walletStore from './wallet-store';

export {
  DynamicProvider,
  DynamicLogin,
  walletStore
};

export default {
  install(app, options = {}) {
    // Register components globally
    app.component('DynamicProvider', DynamicProvider);
    app.component('DynamicLogin', DynamicLogin);

    // Register store module if store is provided
    if (options.store) {
      options.store.registerModule('wallet', walletStore);
    }

    // Set global environment ID
    if (options.environmentId) {
      window.DYNAMIC_ENVIRONMENT_ID = options.environmentId;
    }
  }
};
