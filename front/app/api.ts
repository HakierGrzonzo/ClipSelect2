import { useContext } from 'react'
import { AppClient } from './client/AppClient'
import type { IBackendClient } from './root'
import { BackendContext } from './root'

export const backendURL = (process && process.env.BACKEND) ?? 'http://localhost:8000'

export const backendClient = new AppClient({ BASE: backendURL })

export function useFrontend(): IBackendClient {
  return useContext(BackendContext)
}

