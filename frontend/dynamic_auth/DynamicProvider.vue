<template>
  <DynamicContextProvider :settings="dynamicSettings">
    <slot />
  </DynamicContextProvider>
</template>

<script>
import { DynamicContextProvider } from '@dynamic-labs/sdk-react-core';
import { EthereumWalletConnectors } from '@dynamic-labs/ethereum';

export default {
  name: 'DynamicProvider',
  components: {
    DynamicContextProvider
  },
  inject: ['$store', '$http'],
  data() {
    return {
      dynamicSettings: {
        environmentId: window.DYNAMIC_ENVIRONMENT_ID || '',
        walletConnectors: [EthereumWalletConnectors],
        eventsCallbacks: {
          onAuthSuccess: this.handleAuthSuccess,
          onLogout: this.handleLogout
        },
        settings: {
          environmentId: window.DYNAMIC_ENVIRONMENT_ID || '',
          appName: 'OpenCEX',
          appLogoUrl: '/logo.png'
        }
      }
    };
  },
  methods: {
    async handleAuthSuccess(args) {
      const { authToken, user } = args;

      try {
        // Exchange Dynamic token for OpenCEX tokens
        const response = await this.$http.post('/api/auth/dynamic/', {
          token: authToken
        });

        if (response.data.access) {
          // Store tokens
          localStorage.setItem('token', response.data.access);
          localStorage.setItem('refresh_token', response.data.refresh);
          localStorage.setItem('auth_method', 'wallet');

          // Update Vuex store
          this.$store.commit('LOGIN_SUCCESS');
          this.$store.commit('SET_USER', response.data.user);

          // Redirect to dashboard
          this.$router.push('/account/dashboard');
        }
      } catch (error) {
        console.error('Dynamic auth error:', error);
        this.$notify({
          type: 'error',
          title: 'Authentication Failed',
          text: error.response?.data?.error || 'Failed to authenticate wallet'
        });
      }
    },

    handleLogout() {
      // Clear tokens
      localStorage.removeItem('token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('auth_method');

      // Update Vuex store
      this.$store.commit('LOGOUT');

      // Redirect to login
      this.$router.push('/');
    }
  }
};
</script>
