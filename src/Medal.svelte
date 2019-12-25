<script>
	export let position, right = false;

	const getClass = (pos) => {
		switch (pos) {
			case 1: return "gold";
			case 2: return "silver";
			case 3: return "bronze";
			case '#': return "sum";
			case undefined: return "dnf";
			default:
				if (pos <= 10) return "blue";
				return undefined;
		}
	}
</script>

<div class="medal {getClass(position)} {right ? "right" : undefined}">
	{position || '-'}
</div>

<style>
	.medal {
		font-size: 70%;
		width: 1.5em;
		height: 1.5em;
		text-align: center;
		border-radius: 70%;
	}

	.gold { background-color: #fd5; color: black; }
	.silver { background-color: #ccc; color: black; }
	.bronze { background-color: #963; color: black; }
	.blue { background-color: #34a; color: black; }
	.sum {
		background-image: linear-gradient(135deg, #fd5 20%, #ccc 50%, #963 80%);
		color: black;
	}

	.dnf { opacity: 0.5; }

	.right {
		margin-left: 0.5em;
		margin-top: -0.5em;
	}
</style>
