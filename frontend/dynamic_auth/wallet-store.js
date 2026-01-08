/**
 * Vuex store module for wallet authentication.
 *
 * This module manages wallet-related state and actions.
 * Import and register this module in your main store.
 */

const state = {
  wallets: [],
  primaryWallet: null,
  authMethod: localStorage.getItem('auth_method') || null
};

const mutations = {
  SET_WALLETS(state, wallets) {
    state.wallets = wallets;
    state.primaryWallet = wallets.find(w => w.is_primary) || wallets[0] || null;
  },

  SET_PRIMARY_WALLET(state, wallet) {
    state.primaryWallet = wallet;
  },

  SET_AUTH_METHOD(state, method) {
    state.authMethod = method;
    if (method) {
      localStorage.setItem('auth_method', method);
    } else {
      localStorage.removeItem('auth_method');
    }
  },

  ADD_WALLET(state, wallet) {
    const existingIndex = state.wallets.findIndex(
      w => w.address === wallet.address && w.chain === wallet.chain
    );
    if (existingIndex >= 0) {
      state.wallets[existingIndex] = wallet;
    } else {
      state.wallets.push(wallet);
    }
  },

  REMOVE_WALLET(state, { address, chain }) {
    state.wallets = state.wallets.filter(
      w => !(w.address === address && w.chain === chain)
    );
    // Update primary wallet if removed
    if (state.primaryWallet?.address === address && state.primaryWallet?.chain === chain) {
      state.primaryWallet = state.wallets[0] || null;
    }
  },

  CLEAR_WALLETS(state) {
    state.wallets = [];
    state.primaryWallet = null;
    state.authMethod = null;
    localStorage.removeItem('auth_method');
  }
};

const actions = {
  async fetchUserWallets({ commit }, http) {
    try {
      const token = localStorage.getItem('token');
      if (!token) return;

      const response = await http.get('/api/auth/wallets/', {
        headers: { Authorization: `Bearer ${token}` }
      });

      commit('SET_WALLETS', response.data.wallets);
      commit('SET_AUTH_METHOD', 'wallet');
    } catch (error) {
      console.error('Failed to fetch wallets:', error);
    }
  },

  async linkWallet({ commit }, { http, dynamicToken }) {
    try {
      const token = localStorage.getItem('token');
      const response = await http.post('/api/auth/link-wallet/', {
        token: dynamicToken
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });

      // Refresh wallets list
      const walletsResponse = await http.get('/api/auth/wallets/', {
        headers: { Authorization: `Bearer ${token}` }
      });
      commit('SET_WALLETS', walletsResponse.data.wallets);

      return { success: true, wallets: response.data.wallets };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || 'Failed to link wallet'
      };
    }
  },

  async removeWallet({ commit }, { http, address, chain }) {
    try {
      const token = localStorage.getItem('token');
      await http.delete('/api/auth/wallets/', {
        headers: { Authorization: `Bearer ${token}` },
        data: { address, chain }
      });

      commit('REMOVE_WALLET', { address, chain });
      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || 'Failed to remove wallet'
      };
    }
  },

  clearWalletState({ commit }) {
    commit('CLEAR_WALLETS');
  }
};

const getters = {
  userWallets: state => state.wallets,
  primaryWallet: state => state.primaryWallet,
  authMethod: state => state.authMethod,
  isWalletAuth: state => state.authMethod === 'wallet',
  hasWallets: state => state.wallets.length > 0,

  walletsByChain: state => chain => {
    return state.wallets.filter(w => w.chain === chain);
  },

  formattedPrimaryAddress: state => {
    if (!state.primaryWallet) return null;
    const addr = state.primaryWallet.address;
    return `${addr.slice(0, 6)}...${addr.slice(-4)}`;
  }
};

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
};
