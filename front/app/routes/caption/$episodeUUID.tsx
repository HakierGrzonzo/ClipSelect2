import { backendClient, useFrontend } from '../../api'
import { LoaderFunction, json, LinksFunction } from "@remix-run/node";
import { useLoaderData } from '@remix-run/react';
import { useState } from 'react'
import {Caption} from '../../client/models/Caption'
import {Episode} from '../../client/models/Episode'
import { ClipList, ClipListLinks } from '../../components';

interface IEpisodeAndCaption {
  episode: Episode;
  caption: Caption;
}

export const links: LinksFunction = () => {
  return [...ClipListLinks()];    
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
   const [ selectedCaptions, setSelectedCaptions ] = useState<[Caption, Caption] | undefined>([caption, caption])
   return (
    <div>
      <h1>{episode.name}</h1>
      <div className='split'>
        <div className='split-child'>
          <ClipList captions={episode.captions} selectedCaption={caption} setSelectedRange={setSelectedCaptions}/>
        </div>
        <div className='split-child'>
          {selectedCaptions !== undefined ? (
            selectedCaptions[0].id === selectedCaptions[1].id ? (
                <>
                  <h4>Download a simple clip</h4>
                  <a target='_blank' href={`${frontendURL}/captions/simple?clip_uuid=${selectedCaptions[0].id}&format=gif`}>
                    Download gif
                  </a>
                  <a target='_blank' href={`${frontendURL}/captions/simple?clip_uuid=${selectedCaptions[0].id}`}>
                    Download webm
                  </a>
                </>
              ) : (
                <>
                  <h4>Download a complex clip</h4>
                  <a target='_blank' href={`${frontendURL}/captions/multi?from_clip=${selectedCaptions[0].id}&to_clip=${selectedCaptions[1].id}`}>
                    Download webm
                  </a>
                </>
              )
          ) : (<p>Please select a caption</p>)}
        </div>
      </div>
    </div>
  )
}
