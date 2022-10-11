import type { LoaderFunction } from "@remix-run/node";
import { json } from "@remix-run/node";
import { Link, useLoaderData } from "@remix-run/react";
import { Fragment } from "react";
import { Card } from "../../../components";
import { backendClient, useFrontend } from "../../../api";
import { colors } from "../../../colors";
import type { FullSeries } from "../../../client/models/FullSeries";

export const loader: LoaderFunction = async ({ params }) => {
  const { seriesName } = params;
  const series =
    await backendClient.series.getSeriesByTitleSeriesByTitleTitleGet(
      seriesName
    );
  return json(series);
};

export default function () {
  const series = useLoaderData() as unknown as FullSeries;
  const { frontendURL } = useFrontend();
  return (
    <>
      <h2>Or browse episodes</h2>
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
                .sort((a, b) => a.order - b.order)
                .map((episode) => (
                  <Link
                    key={episode.id}
                    to={`/caption/${episode.id}`}
                    style={{ textDecoration: "none", color: colors.textColor }}
                  >
                    <Card
                      color={colors.linkColor}
                      clickable
                      image={{
                        alt: `Thumbnail for ${episode.name}`,
                        src: `${frontendURL}/episode/thumb/${episode.id}`,
                      }}
                    >
                      <h5>{episode.name}</h5>
                    </Card>
                  </Link>
                ))}
            </div>
          </Card>
        </Fragment>
      ))}
    </>
  );
}
