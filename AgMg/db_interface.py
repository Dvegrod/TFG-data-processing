import psycopg2
import psycopg2.extras as extras
import tensorflow_io as tfio

class Reader:
    def __init__(self, host, database, user, password):
        self.session = psycopg2.connect(f"host={host} dbname={database} user={user} password={password}")
        self.tf_endpoint = f"postgresql://{user}:{password}@{host}?port=5432&dbname={database}"

    def experiment_data(self, experiment_id):
        cursor = self.session.cursor(cursor_factory=extras.RealDictCursor)
        cursor.execute(f"SELECT * FROM public.experimentapp_experiment WHERE id = {experiment_id}")
        return cursor.fetchone()

    def agent_data(self, agent_id):
        cursor = self.session.cursor(cursor_factory=extras.RealDictCursor)
        cursor.execute(f"SELECT * FROM public.experimentapp_agent WHERE id = {agent_id}")
        return cursor.fetchone()

    def number_of_arms(self, edition_id):
        cursor = self.session.cursor(cursor_factory=extras.RealDictCursor)
        cursor.execute(f"SELECT count(*) FROM public.experimentapp_aarm WHERE sub_domain_id = (SELECT sub_domain_id FROM public.experimentapp_edition WHERE id = {edition_id})")
        return cursor.fetchone()['count']

    def edition(self, edition_id, batch):
        return tfio.experimental.IODataset.from_sql(
            query=f"SELECT enabled::int::float, reward, 0::float "
                  f"FROM public.experimentapp_abstractrewardregister WHERE edition_id = {edition_id}"
                  f"ORDER BY date, aarm_id;",
            endpoint=self.tf_endpoint).batch(batch)


class Writer:
    def __init__(self, host, database, user, password, experiment_id):
        self.session = psycopg2.connect(f"host={host} dbname={database} user={user} password={password}")
        self.tf_endpoint = f"postgresql://{user}:{password}@{host}?port=5432&dbname={database}"

        cursor = self.session.cursor(cursor_factory=extras.RealDictCursor)
        cursor.execute(f"INSERT INTO public.experimentapp_episodeexecution (date, experiment_id) VALUES (CURRENT_TIMESTAMP, {experiment_id})")
        cursor = self.session.cursor(cursor_factory=extras.RealDictCursor)
        cursor.execute(f"SELECT id FROM public.experimentapp_episodeexecution WHERE date = (SELECT max(date) FROM public.experimentapp_episodeexecution)")
        self.episode_id = cursor.fetchone()['id']

    async def save_step(self, iteration, performance, reward):
        cursor = self.session.cursor(cursor_factory=extras.RealDictCursor)
        cursor.execute(f"INSERT INTO public.experimentapp_executionresult (iteration, performance, reward, episode_id) VALUES ({iteration}, {performance}, {reward}, {self.episode_id})")