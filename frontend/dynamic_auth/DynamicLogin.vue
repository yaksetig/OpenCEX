<template>
  <div class="dynamic-login">
    <div class="login-container">
      <div class="login-header">
        <img :src="logoUrl" alt="Logo" class="logo" />
        <h1>{{ $t('auth.connect_wallet') || 'Connect Wallet' }}</h1>
        <p class="subtitle">
          {{ $t('auth.connect_wallet_subtitle') || 'Connect your wallet to access the exchange' }}
        </p>
      </div>

      <div class="wallet-connect-section">
        <DynamicWidget />
      </div>

      <div class="info-section">
        <div class="info-item">
          <span class="icon">🔒</span>
          <span>{{ $t('auth.secure_connection') || 'Secure Connection' }}</span>
        </div>
        <div class="info-item">
          <span class="icon">⚡</span>
          <span>{{ $t('auth.instant_access') || 'Instant Access' }}</span>
        </div>
        <div class="info-item">
          <span class="icon">🌐</span>
          <span>{{ $t('auth.multi_chain') || 'Multi-Chain Support' }}</span>
        </div>
      </div>

      <div class="supported-wallets">
        <p>{{ $t('auth.supported_wallets') || 'Supported Wallets' }}</p>
        <div class="wallet-icons">
          <span title="MetaMask">🦊</span>
          <span title="WalletConnect">🔗</span>
          <span title="Coinbase Wallet">💰</span>
          <span title="Rainbow">🌈</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { DynamicWidget } from '@dynamic-labs/sdk-react-core';

export default {
  name: 'DynamicLogin',
  components: {
    DynamicWidget
  },
  computed: {
    logoUrl() {
      return window.LOGO_URL || '/logo.png';
    }
  }
};
</script>

<style scoped>
.dynamic-login {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  padding: 20px;
}

.login-container {
  max-width: 420px;
  width: 100%;
  background: #ffffff;
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.logo {
  width: 80px;
  height: 80px;
  margin-bottom: 16px;
}

.login-header h1 {
  font-size: 24px;
  font-weight: 600;
  color: #1a1a2e;
  margin: 0 0 8px 0;
}

.subtitle {
  font-size: 14px;
  color: #666;
  margin: 0;
}

.wallet-connect-section {
  margin-bottom: 32px;
}

.info-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 24px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  color: #333;
}

.info-item .icon {
  font-size: 18px;
}

.supported-wallets {
  text-align: center;
  padding-top: 16px;
  border-top: 1px solid #eee;
}

.supported-wallets p {
  font-size: 12px;
  color: #999;
  margin: 0 0 12px 0;
}

.wallet-icons {
  display: flex;
  justify-content: center;
  gap: 16px;
  font-size: 24px;
}

.wallet-icons span {
  cursor: default;
  transition: transform 0.2s;
}

.wallet-icons span:hover {
  transform: scale(1.2);
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
  .login-container {
    background: #1e1e2e;
  }

  .login-header h1 {
    color: #ffffff;
  }

  .subtitle {
    color: #aaa;
  }

  .info-section {
    background: #2a2a3e;
  }

  .info-item {
    color: #ddd;
  }

  .supported-wallets {
    border-top-color: #333;
  }
}
</style>
