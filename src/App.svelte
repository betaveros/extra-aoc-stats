<script>
	import debounce from 'lodash.debounce';

	import Medal from './Medal.svelte';

	import data2015 from './2015.json';
	import data2016 from './2016.json';
	import data2017 from './2017.json';
	import data2018 from './2018.json';
	import data2019 from './2019.json';
	import data2020 from './2020.json';
	import data2021 from './2021.json';

	const yearList = [2015, 2016, 2017, 2018, 2019, 2020, 2021];

	let yearDataDict = {
		2015: data2015,
		2016: data2016,
		2017: data2017,
		2018: data2018,
		2019: data2019,
		2020: data2020,
		2021: data2021,
	};

	let selectedYear = 2020;

	let omit2018_6 = true;
	let omit2020_1 = true;

	$: scoreData = yearDataDict[selectedYear];

	const processYear = (rawData) => {
		let playerInfos = {};
		let maxDay = 0;
		let partFinishSeconds = {};

		// optimization (faster than forEach) ???
		const sl = rawData.length;
		for (let i = 0; i < sl; i++) {
			const { d: day, l: leaderboard } = rawData[i];

			maxDay = Math.max(maxDay, day);

			// optimization (faster than forEach) ???
			const ll = leaderboard.length;
			for (let j = 0; j < ll; j++) {
				const entry = leaderboard[j];

				const { n: name, i: img, h: href, s: supporter, p: sponsor } = entry.u;
				const { p: part, n: position, s: seconds } = entry;

				let info = playerInfos[name] || {
					performances: {},
				};
				if (supporter) { info.supporter = true; }
				if (sponsor) { info.sponsor = sponsor; }
				if (img) { info.img = img; }
				if (href) { info.href = href; }

				info.performances[day] = info.performances[day] || {};
				info.performances[day][part] = { position, seconds };

				partFinishSeconds[day] = partFinishSeconds[day] || {};
				partFinishSeconds[day][part] = Math.max(
					partFinishSeconds[day][part] || 0,
					seconds);

				playerInfos[name] = info;
			}
		}

		return { playerInfos, maxDay, partFinishSeconds };
	};

	$: processedYearData = processYear(scoreData);
	
	const getPosition = (info, day, part) => {
		if (info.performances[day] && info.performances[day][part]) {
			return info.performances[day][part].position;
		}
	}

	const oneRange = (end) => {
		let ret = [];
		for (let i = 1; i <= end; i++) ret.push(i);
		return ret;
	};

	let selectedPart = 0;

	const makeUnsortedScoreList = (yearData, selPart, omits) => Object.entries(yearData.playerInfos).map(([name, info]) => {
		let score = 0, totalSeconds = 0, count = 0, dnfPenalty = 0;
		let medalCounts = { 1: 0, 2: 0, 3: 0 };

		for (let day = 1; day <= yearData.maxDay; day++) {
			if (omits[`${selectedYear}-${day}`]) continue;

			for (let part = 1; part <= 2; part++) {
				if (selPart && selPart !== part) continue;

				if (info.performances[day] && info.performances[day][part]) {
					const { position, seconds } = info.performances[day][part];
					score += 101 - position;
					totalSeconds += seconds;
					count++;

					if (position <= 3) {
						medalCounts[position]++;
					}
				} else {
					dnfPenalty += yearData.partFinishSeconds[day][part];
				}
			}
		}

		const medalScore = 1000000 * medalCounts[1] + 1000 * medalCounts[2] + medalCounts[3];
		const medalTotalScore = 1000000000 * (medalCounts[1] + medalCounts[2] + medalCounts[3]) + medalScore;

		return {
			name,
			img: info.img,
			href: info.href,
			score,
			totalSeconds,
			count,
			dnfPenalty,
			combinedNegativePenalty: -(totalSeconds + dnfPenalty),
			medalCounts,
			medalScore,
			medalTotalScore,
			supporter: info.supporter,
			sponsor: info.sponsor,
			performances: info.performances,
		};
	});

	$: originalScoreList = makeUnsortedScoreList(processedYearData, selectedPart, {
		'2018-6': omit2018_6,
		'2020-1': omit2020_1,
	});

	let sortKey = "score"; // sort descending by it

	$: scoreList = originalScoreList.slice().sort((a, b) => (b[sortKey] - a[sortKey]));

	let showMedals = false;

	let christmasMode = false;

	let renderedData = { scoreList: [], maxDay: 0, selectedPart: 0, selectedYear, showMedals, christmasMode };
	const updateRenderedData = debounce((data) => { renderedData = data; }, 50);
	$: updateRenderedData({
		scoreList,
		maxDay: processedYearData.maxDay,
		selectedPart,
		selectedYear,
		showMedals,
		christmasMode,
	});

	const pad2 = (n) => {
		const s = String(n);
		return '0'.repeat(Math.max(2 - s.length, 0)) + s;
	};

	const formatSeconds = (ss) => {
		const h = Math.floor(ss / 3600);
		const m = Math.floor((ss % 3600) / 60);
		const s = ss % 60;
		return `${pad2(h)}:${pad2(m)}:${pad2(s)}`;
	};

</script>

<main>
	<div>
		<a href="https://adventofcode.com/">Advent of Code</a> Extra Leaderboard (by <a href="https://beta.vero.site/">betaveros</a> / inspirations: <a href="http://www.maurits.vdschee.nl/scatterplot/medals.html">mevdschee</a>, <a href="https://www.reddit.com/r/adventofcode/comments/a9dh93/2018_complete_global_leaderboard/">/u/mebeim</a>, etc.)
	<div>
		Year:
		{#each yearList as year}
		{' '}
		<label>
			<input type=radio bind:group={selectedYear} value={year}>{year}
		</label>
		{/each}

		{#if selectedYear === 2018}
		<label>
			<input type=checkbox bind:checked={omit2018_6}>Omit Day 6
		</label>
		{/if}
		{#if selectedYear === 2020}
		<label>
			<input type=checkbox bind:checked={omit2020_1}>Omit Day 1
		</label>
		{/if}
	</div>
	<div>
		Part:
		<label>
			<input type=radio bind:group={selectedPart} value={1}>1
		</label>

		<label>
			<input type=radio bind:group={selectedPart} value={2}>2
		</label>

		<label>
			<input type=radio bind:group={selectedPart} value={0}>Both
		</label>
	</div>

	<div>
		Sort by:
		<label>
			<input type=radio bind:group={sortKey} value={"score"}>Score
		</label>

		<label>
			<input type=radio bind:group={sortKey} value={"count"}># Leaderboard
		</label>

		<label>
			<input type=radio bind:group={sortKey} value={"combinedNegativePenalty"}>Σ min(T,100<sup>th</sup>)
		</label>

		<label>
			<input type=radio bind:group={sortKey} value={"medalScore"}>Medals (G&gg;S&gg;B)
		</label>

		<label>
			<input type=radio bind:group={sortKey} value={"medalTotalScore"}>Medals (#)
		</label>

		<label>
			<input type=checkbox bind:checked={showMedals}>Show All Leaderboards/Medals (slower)
		</label>

		<label>
			<input type=checkbox bind:checked={christmasMode}>CHRISTMAS MODE
		</label>
	</div>
	<table class={renderedData.christmasMode ? "christmas" : undefined}>
		<tr>
			<th>#</th>
			<th>Score</th>
			<th class="img">🖼️</th>
			<th>Name</th>
			<th title="Total time for all leaderboard appearances">Σ Time</th>
			<th title="Number of leaderboard appearances"># Ls</th>
			<th title="Total time for both parts of all days, using the 100th place's time if not on the leaderboard" class="combined">Σ min(T,100<sup>th</sup>)</th>
			<th class="medal"><Medal position={1} /></th>
			<th class="medal"><Medal position={2} /></th>
			<th class="medal"><Medal position={3} /></th>
			<th class="medal"><Medal position="#" /></th>
			{#if renderedData.showMedals}
				{#each oneRange(renderedData.maxDay) as day}
					<th class="day"><a href="https://adventofcode.com/{renderedData.selectedYear}/leaderboard/day/{day}">{day}</a></th>
				{/each}
			{/if}
		</tr>
		{#each renderedData.scoreList as scoreInfo, i}
			<tr>
				<td class="position">{i+1})</td>
				<td class="score rb">{scoreInfo.score}</td>
				<td class="img">
					{#if scoreInfo.img}
						<img src={scoreInfo.img} alt="Profile picture for {scoreInfo.name}" />
					{/if}
				</td>
				<td class="name">
					{#if scoreInfo.href}
						<a href={scoreInfo.href} class="user">{scoreInfo.name}</a>
					{:else}
						{scoreInfo.name}
					{/if}
					{#if scoreInfo.supporter}
						{' '}<a href="https://adventofcode.com/{renderedData.selectedYear}/support" class="support">(AoC++)</a>
					{/if}
					{#if scoreInfo.sponsor}
						{' '}<a href={scoreInfo.sponsor} class="sponsor">(Sponsor)</a>
					{/if}
				</td>
				<td class="score">{formatSeconds(scoreInfo.totalSeconds)}</td>
				<td class="score">{scoreInfo.count}</td>
				<td class="score rb">{formatSeconds(scoreInfo.totalSeconds + scoreInfo.dnfPenalty)}</td>
				<td class="medal">{scoreInfo.medalCounts[1]}</td>
				<td class="medal">{scoreInfo.medalCounts[2]}</td>
				<td class="medal">{scoreInfo.medalCounts[3]}</td>
				<td class="medal">{scoreInfo.medalCounts[1] + scoreInfo.medalCounts[2] + scoreInfo.medalCounts[3]}</td>
				{#if renderedData.showMedals}
					{#each oneRange(renderedData.maxDay) as day}
						<td class="pos">
							{#if renderedData.selectedPart !== 2}
								<Medal position={getPosition(scoreInfo, day, 1)} />
							{/if}
							{#if renderedData.selectedPart !== 1}
								<Medal position={getPosition(scoreInfo, day, 2)} right={renderedData.selectedPart === 0} />
							{/if}
						</td>
					{/each}
				{/if}
			</tr>
		{/each}
	</table>
</main>

<style>
	td, th { white-space: nowrap; }

	th.day { padding: 0; font-size: 70%; }
	th.img { padding: 0 0.5em; }
	th.medal, td.medal { padding: 0 0.5em; text-align: right; }

	td.position { text-align: right; }
	td.name { text-align: left; }
	td.score { text-align: right; }
	td.rb { padding-right: 0.5em; }

	th.combined { padding-left: 1em; }

	td.pos { text-align: center; padding: 0 0.2em; }

	table {
		border-collapse: collapse;
	}
	tr + tr { border-top: 1px solid rgba(255, 255, 255, 0.2); }

	.christmas tr:nth-child(3n) > :nth-child(3n), .christmas tr:nth-child(3n+1) > :nth-child(3n+1), .christmas tr:nth-child(3n+2) > :nth-child(3n+2) {
		color: #cfc;
	}
	.christmas tr:nth-child(3n) > :nth-child(3n+1), .christmas tr:nth-child(3n+1) > :nth-child(3n+2), .christmas tr:nth-child(3n+2) > :nth-child(3n) {
		color: #fcc;
	}
	.christmas tr:nth-child(3n) > :nth-child(3n+1) a.user:link, .christmas tr:nth-child(3n+1) > :nth-child(3n+2) a.user:link, .christmas tr:nth-child(3n+2) > :nth-child(3n) a.user:link {
		color: #d00;
	}
	.christmas tr:nth-child(3n) > :nth-child(3n+1) a.user:visited, .christmas tr:nth-child(3n+1) > :nth-child(3n+2) a.user:visited, .christmas tr:nth-child(3n+2) > :nth-child(3n) a.user:visited {
		color: #b00;
	}

	img {
		height: 1em;
	}
	td.img {
		text-align: center; vertical-align: middle;
		max-width: 1em;
		overflow: hidden;
		color: #999;
	}

	a.support { color: #ff6; }
	a.sponsor { color: #8ad; }
</style>
