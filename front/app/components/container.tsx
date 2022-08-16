import type { ReactNode } from 'react'

interface IProps {
  children: ReactNode
}

export function Container(props: IProps) {
  return (
    <main>
      {props.children}
    </main>
  )
}
