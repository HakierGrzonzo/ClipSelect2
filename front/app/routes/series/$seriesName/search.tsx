import { LinksFunction, LoaderFunction, redirect } from "@remix-run/node";
import { json } from "@remix-run/node";
import { Link, useLoaderData } from "@remix-run/react";
import { Fragment } from "react";
import {
  Card,
  CardLinks,
  ExpandableCard,
  ExpandableCardLinks,
} from "../../../components";
import { backendClient, useFrontend } from "../../../api";
import { colors } from "../../../colors";
import type { CaptionSeries } from "../../../client/models/CaptionSeries";

export const links: LinksFunction = () => {
  return [...ExpandableCardLinks(), ...CardLinks()];
};

export const loader: LoaderFunction = async ({ params, request }) => {
  const { seriesName } = params;
  const query = new URL(request.url).searchParams.get("query");
  if (!query) {
    throw redirect(`/series/${encodeURI(seriesName!)}`)
  }
  const series = await backendClient.series.searchSeriesSeriesSearchTitleGet(
    seriesName!,
    query!
  );
  return json(series);
};

export default function () {
  const series = useLoaderData() as unknown as CaptionSeries;
  const { frontendURL } = useFrontend();
  return (
    <>
      <h2>Results</h2>
      {series.subseries.map((subserie) => (
        <Fragment key={subserie.id}>
          <Card color={colors.textColor}>
            <h3>{subserie.name}</h3>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, 50ex)",
              }}
            >
              {subserie.episodes
                .sort(
                  (a, b) =>
                    b.captions.length - a.captions.length || a.order - b.order
                )
                .map((episode) => (
                  <Fragment key={episode.id}>
                    <ExpandableCard
                      color={colors.accentColor}
                      image={{
                        alt: `Thumbnail for ${episode.name}`,
                        src: `${frontendURL}/episode/thumb/${episode.id}`,
                      }}
                      header={
                        <div
                          style={{
                            display: "flex",
                            gap: ".5em",
                            justifyContent: "space-around",
                            flexDirection: "column",
                          }}
                        >
                          <div style={{ fontWeight: 700 }}>{episode.name}</div>
                          <div>{episode.captions.length} clips found</div>
                        </div>
                      }
                    >
                      <ul>
                        {episode.captions
                          .sort((a, b) => a.order - b.order)
                          .map((caption) => (
                            <li key={caption.id}>
                              <Link
                                to={`/caption/${episode.id}#${caption.id}`}
                                dangerouslySetInnerHTML={{
                                  __html: caption.text,
                                }}
                              />
                            </li>
                          ))}
                      </ul>
                    </ExpandableCard>
                  </Fragment>
                ))}
            </div>
          </Card>
        </Fragment>
      ))}
    </>
  );
}
