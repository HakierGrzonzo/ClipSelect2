import type {
  LinksFunction,
  LoaderFunction,
  MetaFunction,
} from "@remix-run/node";
import { json } from "@remix-run/node";
import { useLoaderData } from "@remix-run/react";
import { useReducer, useEffect } from "react";
import { backendClient, useFrontend } from "../../api";
import type { Caption } from "../../client/models/Caption";
import type { Episode } from "../../client/models/Episode";
import styles from "../../caption.css";
import { ClipList, ClipListLinks, Trange } from "../../components";

interface IEpisodeAndCaption {
  episode: Episode;
}

const reducer = (captions: Caption[]) => {
  const getCaption = (order: number): Caption =>
    captions.find((c) => c.order === order);
  return (state: Trange, action: Caption | undefined): Trange => {
    if (action === undefined) return undefined;
    if (state === undefined) return [action];
    if (state.length === 1) {
      if (state[0].id !== action.id)
        return [...state, action].sort((a, b) => a.order - b.order) as Trange;
      else return undefined;
    }
    const [start, stop] = state;
    if (action.order > stop.order) return [start, action];
    if (action.order < start.order) return [action, stop];
    if (action.order === start.order)
      return [getCaption(start.order + 1), stop];
    if (action.order === stop.order)
      return [start, getCaption(start.order + 1)];
    const mid = (start.order + stop.order) / 2;
    if (action.order > mid) return [start, action];
    if (action.order < mid) return [action, stop];
    if (action.order === mid) return [action];
    return state;
  };
};

export const links: LinksFunction = () => {
  return [...ClipListLinks(), { rel: "stylesheet", href: styles }];
};

export const loader: LoaderFunction = async ({ params }) => {
  const { episodeUUID } = params;
  const episode =
    await backendClient.episode.getEpisodeByUuidEpisodeGetEpisodeUuidGet(
      episodeUUID
    );
  return json({
    episode,
  });
};

export const meta: MetaFunction = (data) => {
  const { episode } = data.data;
  return {
    title: `ClipSelect | ${episode.name}`,
    description: `Generate clips for ${episode.name}!`,
    "og:image": `https://clipapi.grzegorzkoperwas.site/episode/thumb/${episode.id}`,
  };
};

export default function () {
  const { episode } = useLoaderData() as IEpisodeAndCaption;
  const { frontendURL } = useFrontend();
  const [selectedCaptions, setSelectedCaptions] = useReducer(
    reducer(episode.captions),
    undefined
  );
  useEffect(() => {
    if (process) return;
    const captionId = document.location.hash.slice(1);
    const captionCandidates = episode.captions.filter(
      (caption) => caption.id === captionId
    );
    if (captionCandidates.length !== 1) return;
    setSelectedCaptions(...(captionCandidates as [Caption]));
  }, [process]);

  return (
    <div>
      <h1>{episode.name}</h1>
      <div className="caption-split">
        <div className="split-child">
          <ClipList
            captions={episode.captions}
            selectedRange={selectedCaptions}
            setSelectedRange={setSelectedCaptions}
          />
        </div>
        <div className="download-buttons download-menu">
          {selectedCaptions !== undefined ? (
            selectedCaptions.length === 1 ? (
              <>
                <h4>Download a simple clip</h4>
                <a
                  target="_blank"
                  href={`${frontendURL}/captions/simple?clip_uuid=${selectedCaptions[0].id}&format=gif`}
                  rel="noreferrer"
                >
                  Download gif
                </a>
                <a
                  target="_blank"
                  href={`${frontendURL}/captions/simple?clip_uuid=${selectedCaptions[0].id}`}
                  rel="noreferrer"
                >
                  Download webm
                </a>
                <a onClick={() => setSelectedCaptions(undefined)}>
                  Clear selection
                </a>
              </>
            ) : (
              <>
                <h4>Download a complex clip</h4>
                <a
                  target="_blank"
                  href={`${frontendURL}/captions/multi?from_clip=${selectedCaptions[0].id}&to_clip=${selectedCaptions[1].id}`}
                  rel="noreferrer"
                >
                  Download webm
                </a>
                <a onClick={() => setSelectedCaptions(undefined)}>
                  Clear selection
                </a>
              </>
            )
          ) : (
            <p>Please select a caption</p>
          )}
        </div>
      </div>
    </div>
  );
}
