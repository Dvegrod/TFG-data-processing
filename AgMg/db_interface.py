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
    def __init__(self, host, database, user, password, edition):
        self.session = psycopg2.connect(f"host={host} dbname={database} user={user} password={password}")
        self.tf_endpoint = f"postgresql://{user}:{password}@{host}?port=5432&dbname={database}"
        self.edition = edition
        self.episode_id = None

    def register_execution(self, experiment_id):
        # CHECK UF THE EXPERIMENT IS NOT RUNNING ALREADY
        with self.session.cursor() as curs:
            curs.execute(f"SELECT running FROM public.experimentapp_experiment WHERE id = {experiment_id}")
            if curs.fetchone()[0]:
                raise RuntimeError("Experiment already in execution.")
            else:
                curs.execute(f"UPDATE public.experimentapp_experiment SET running = true, completed_iterations = 1 WHERE id = {experiment_id}")
        cursor = self.session.cursor(cursor_factory=extras.RealDictCursor)
        cursor.execute(
            f"INSERT INTO public.experimentapp_episodeexecution (date, experiment_id) VALUES (CURRENT_TIMESTAMP, {experiment_id})")
        cursor = self.session.cursor(cursor_factory=extras.RealDictCursor)
        cursor.execute(
            f"SELECT id FROM public.experimentapp_episodeexecution WHERE date = (SELECT max(date) FROM public.experimentapp_episodeexecution)")
        self.episode_id = cursor.fetchone()['id']
        self.session.commit()
        self.experiment_id = experiment_id
        # Convert iteration to date
        with self.session.cursor() as curs:
            curs.execute(f"SELECT date FROM public.experimentapp_abstractrewardregister WHERE edition_id = {self.edition} GROUP BY date ORDER BY date")
            self.datelist = curs.fetchall()
        # Convert action to aarm
        with self.session.cursor() as curs:
            curs.execute(f"SELECT id FROM public.experimentapp_aarm WHERE sub_domain_id IN (SELECT sub_domain_id FROM public.experimentapp_experiment WHERE id = {self.experiment_id})")
            self.aarm_list = curs.fetchall()
        print(self.aarm_list)
        return self.episode_id

    def save_step(self, iteration, performance, reward, aarm):
        cursor = self.session.cursor(cursor_factory=extras.RealDictCursor)
        date = self.datelist[iteration][0]
        print(aarm)
        aarm = self.aarm_list[aarm[0]][0]
        # Insert step
        cursor.execute(f"INSERT INTO public.experimentapp_executionresult (iteration, performance, reward, episode_id, action_id) VALUES ('{date}', {performance}, {reward}, {self.episode_id}, {aarm})")
        cursor.execute(f"UPDATE public.experimentapp_experiment SET completed_iterations = completed_iterations + 1 WHERE id = {self.experiment_id}")
        self.session.commit()

    def finish_execution(self, experiment_id):
        with self.session.cursor() as curs:
            curs.execute(f"UPDATE public.experimentapp_experiment SET running = false WHERE id = {experiment_id}")
            self.session.commit()
