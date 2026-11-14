// export const API_URL = import.meta.env.VITE_API_URL || "http://localhost:3000";
export const API_URL = "https://7m4g0csiic.execute-api.us-east-1.amazonaws.com"
export const SKIN_TYPES = [
  { id: "dry", label: "Dry", icon: "🌵" },
  { id: "oily", label: "Oily", icon: "💧" },
  { id: "combination", label: "Combination", icon: "☯️" },
  { id: "sensitive", label: "Sensitive", icon: "🌸" },
];

export const AMPLIFY_OUTPUTS = {
  Auth: {
    Cognito: {
      userPoolClientId: "51i8a4bvc3ff340sl6spb7pmoh",
      userPoolId: "us-east-1_wfofZXzaq",
      signUpVerificationMethod: "code",
      userAttributes: {
        email: {
          required: true,
        },
      },
      loginWith: {
        oauth: {
          domain: 'product-scanner.auth.us-east-1.amazoncognito.com',
          scopes: ['openid', 'email', 'profile'],
          redirectSignIn: ['http://localhost:5173'],
          redirectSignOut: ['http://localhost:5173'],
          responseType: 'code',
        },
        username: true,
        email: true
      },
      passwordPolicy: {
        minLength: 8,
        requireNumbers: true,
        requireSymbols: true,
      },

    }
  }
}
