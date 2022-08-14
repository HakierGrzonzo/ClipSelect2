import { Card } from '../../../components';
import { backendClient, frontendURL } from '../../../api'
import { colors } from '../../../colors'
import { LoaderFunction, json } from "@remix-run/node";
import { useLoaderData } from '@remix-run/react';
import { FullSeries } from '../../../client/models/FullSeries';

export const loader: LoaderFunction = async ({params}) => {
  const {seriesName} = params;
  const series = await backendClient.series.getSeriesByTitleSeriesByTitleTitleGet(seriesName)
  return json(series)
}

export default function() {
  const series = useLoaderData() as unknown as FullSeries;
  return (
    <>
      <h2>Or browse episodes</h2>
      {series.subseries.map(subserie => (
        <Card color={colors.textColor}>
          <h3>{subserie.name}</h3>
          <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, 50ex)',
            }}>
            {subserie.episodes.sort((a, b) => a.order - b.order).map(episode => (
              <Card color={colors.accentColor} image={{
                  alt: `Thumbnail for ${episode.name}`,
                  src: `${frontendURL}/episode/thumb/${episode.id}`,
                }}>
                {episode.name}
              </Card>
            ))}
          </div>
        </Card>
      ))}
    </>
  )
}
