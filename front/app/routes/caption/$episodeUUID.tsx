import { backendClient, useFrontend } from '../../api'
import { LoaderFunction, json } from "@remix-run/node";
import { useLoaderData } from '@remix-run/react';
import {Caption} from '../../client/models/Caption'
import {Episode} from '../../client/models/Episode'

interface IEpisodeAndCaption {
  episode: Episode;
  caption: Caption;
}

export const loader: LoaderFunction = async ({params, request}) => {
  const { episodeUUID } = params;
  const query = new URL(request.url).searchParams.get('caption')
  const episode = await backendClient.episode.getEpisodeByUuidEpisodeGetEpisodeUuidGet(episodeUUID)
  const caption = episode.captions.find(c => query == c.id)
  if (caption === undefined) {
    throw Error('Caption not found')
  }
  return json({
    episode,
    caption, 
  })
}

export default function() {
   const {episode, caption} = useLoaderData() as IEpisodeAndCaption;
   const { frontendURL } = useFrontend();
   return <div>
      <h1>{episode.name} - {caption.text}</h1>
      <img src={`${frontendURL}/captions/simple?format=gif&clip_uuid=${caption.id}`}/>
    </div>
}
