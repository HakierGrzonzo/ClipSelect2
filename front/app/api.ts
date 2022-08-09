import { AppClient } from './client/AppClient';

export const backendClient = new AppClient({BASE: 'http://cliper'})
export const frontendClient = new AppClient({BASE: ''})

