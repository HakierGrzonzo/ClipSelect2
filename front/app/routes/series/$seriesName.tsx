import { Card, CardLinks } from '../../components';
import { backendClient } from '../../api'
import { colors } from '../../colors'
import { LoaderFunction, LinksFunction, json } from "@remix-run/node";
import { Form, Outlet, useLoaderData } from '@remix-run/react';
import { Series } from '../../client/models/Series';

export const links: LinksFunction = () => {
  return [...CardLinks()]
}

interface ISeriesWithParam {
  query: string | undefined;
  series: Series;
}

export const loader: LoaderFunction = async ({params, request}) => {
  const {seriesName} = params;
  const query = new URL(request.url).searchParams.get('query')
  const series = await backendClient.series.getSeriesByTitleSeriesByTitleTitleGet(seriesName)
  return json({
      series,
      query,
    })
}

export default function() {
  const {series, query} = useLoaderData() as unknown as ISeriesWithParam
  return (
    <>
      <h1>{series.name}</h1>
      <div class='split'>
        <div className={'split-child'} style={{borderStyle: 'solid', borderWidth: '0 2px 0 0', borderColor: colors.accentColor}}>
          <h2>Search for quote</h2>
          <Form method='get' action="search">
            <label aria-label="Search">
              <input type='text' name="query" id="query" default={query}/>
            </label>
            <input type="submit" value="Search"/>
          </Form>
        </div>
        <div className={'split-child'}>
          <Outlet/>
        </div>
      </div>
    </>
  )
}