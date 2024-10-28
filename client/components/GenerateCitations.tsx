export const GenerateCitations = ({
  citationsArray,
}: {
  citationsArray?: { citation: string; link: string }[];
}) => {
  return (
    citationsArray && (
      <ol className="list-decimal pl-4 space-y-2">
        {citationsArray.map((item, index) => (
          <li key={index} className="text-gray-700">
            {item.citation}{" "}
            <a
              href={item.link}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:underline"
            >
              {item.link}
            </a>
            .
          </li>
        ))}
      </ol>
    )
  );
};
