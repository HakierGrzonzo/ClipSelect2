import { json, LoaderFunction } from '@remix-run/node'
import { Form, useLoaderData } from '@remix-run/react'
import { DataService, Episode } from '../../../client'

export const loader: LoaderFunction = async (props) => {
  const { episode: episode_uuid } = props.params;
  const url = new URL(props.request.url)
  const episode = await DataService.getEpisodeByUuidEpisodeGet(episode_uuid, url.searchParams.get('search') || '')
  return json(episode)
}

export default function Series() {
  const episode = useLoaderData() as unknown as Episode
  return (
    <div>
        <h3>{episode.name}</h3>
        <Form method="get">
            <input name="search" type="text"/>
            <button type="submit">Update</button>
        </Form>
        <p>
            { episode.captions.length === 0 ? 'Sorry we found no clips' : 'wooo'}
        </p>
    </div>
  )
}
