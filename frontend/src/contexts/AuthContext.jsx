import React, { createContext, useReducer, useCallback } from 'react';

export const AuthContext = createContext();

const initialState = {
  user: null,
  token: localStorage.getItem('access_token') || null,
  isAuthenticated: !!localStorage.getItem('access_token'),
  loading: false,
  error: null,
};

function authReducer(state, action) {
  switch (action.type) {
    case 'LOGIN_START':
      return { ...state, loading: true, error: null };
    case 'LOGIN_SUCCESS':
      return {
        ...state,
        user: action.payload.user,
        token: action.payload.token,
        isAuthenticated: true,
        loading: false,
      };
    case 'LOGIN_ERROR':
      return { ...state, error: action.payload, loading: false };
    case 'LOGOUT':
      return { ...state, user: null, token: null, isAuthenticated: false };
    case 'RESTORE_TOKEN':
      return { ...state, token: action.payload, isAuthenticated: !!action.payload };
    default:
      return state;
  }
}

export function AuthProvider({ children }) {
  const [state, dispatch] = useReducer(authReducer, initialState);

  const login = useCallback(async (username, password) => {
  dispatch({ type: 'LOGIN_START' });
  try {
    const response = await fetch('http://localhost:8000/api/auth/login/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),  // Change email → username
    });

    if (!response.ok) throw new Error('Login failed');

    const data = await response.json();
    localStorage.setItem('access_token', data.token);  // Change data.access → data.token

    dispatch({
      type: 'LOGIN_SUCCESS',
      payload: { token: data.token, user: data.user },  // Change data.access → data.token
    });

    return data;
  } catch (error) {
    dispatch({ type: 'LOGIN_ERROR', payload: error.message });
    throw error;
  }
}, []);

  const logout = useCallback(() => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    dispatch({ type: 'LOGOUT' });
  }, []);

  const value = {
    ...state,
    login,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}