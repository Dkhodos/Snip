const months = [
	"Jan",
	"Feb",
	"Mar",
	"Apr",
	"May",
	"Jun",
	"Jul",
	"Aug",
	"Sep",
	"Oct",
	"Nov",
	"Dec",
];

export function formatDate(dateStr: string): string {
	const date = new Date(dateStr);
	return `${months[date.getMonth()]} ${date.getDate()}`;
}
