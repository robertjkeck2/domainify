import json
import os
import sys
import platform
import asyncio
import time


class DomainFinder(object):
    def __init__(self):
        self.command = 'whois'
    
    def search(self, urls):
        """Searches for available domains from a list of domain names"""
        tasks = []
        available = []
        for url in urls:
            tasks.append(self._run_command(
                *[self.command, url]))
        results = self._run_asyncio_commands(
            tasks, max_concurrent_tasks=50)
        result_list = list(zip(urls, results))
        for result in result_list:
            if result[1]:
                available.append(result[0])
        return available

    def _check_availability(self, text):
        """Determines is domain is available from WHOIS"""
        source_start = text.find('No match')
        if source_start >= 0:
            return True
        return False

    async def _run_command(self, *args):
        """Run command in subprocess"""
        process = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE)
        stdout, stderr = await process.communicate()
        result = stdout.decode().strip()
        return self._check_availability(result)

    def _make_chunks(self, l, n):
        """Yield successive n-sized chunks from l."""
        if sys.version_info.major == 2:
            for i in xrange(0, len(l), n):
                yield l[i:i + n]
        else:
            for i in range(0, len(l), n):
                yield l[i:i + n]

    def _run_asyncio_commands(self, tasks, max_concurrent_tasks=0):
        """Run tasks asynchronously using asyncio and return results"""
        all_results = []
        if max_concurrent_tasks == 0:
            chunks = [tasks]
        else:
            chunks = self._make_chunks(l=tasks, n=max_concurrent_tasks)
        for tasks_in_chunk in chunks:
            if platform.system() == 'Windows':
                loop = asyncio.ProactorEventLoop()
                asyncio.set_event_loop(loop)
            else:
                loop = asyncio.get_event_loop()
            commands = asyncio.gather(*tasks_in_chunk)
            results = loop.run_until_complete(commands)
            all_results += results
        return all_results

if __name__ == '__main__':
    available = []
    word_list = []
    with open('search_output.json', 'r') as infile:
        words = json.load(infile)
    for word in words:
        word_list.append(str(word) + '.com')
    finder = DomainFinder()
    for i in range(0, int(len(word_list)), 30):
        available_words = finder.search(word_list[i:i+29])
        available.append(available_words)
        print(available_words)
        time.sleep(5)
    print(available)

    
