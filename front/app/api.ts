import { AppClient } from './client/AppClient';

export const backendURL = 'http://localhost:8000'

export const backendClient = new AppClient({BASE: backendURL})
export const frontendClient = new AppClient({BASE: ''})

