export const BotAvatar: React.FC<{ isLoading: boolean }> = ({
  isLoading = false,
}) => {
  return (
    <div className="mb-20 flex h-full w-full justify-center">
      {isLoading ? (
        <div className="flex aspect-square h-full items-center justify-center overflow-hidden rounded-full bg-gray-400">
          <div className="h-32 w-32 animate-spin rounded-full border-8 border-dashed border-gray-100 border-t-transparent" />
        </div>
      ) : (
        <div className="flex aspect-square h-full items-center overflow-hidden rounded-full bg-blue-300">
          <video autoPlay className="h-full w-full object-cover" loop>
            <source src="placeholder.mp4" type="video/mp4" />
          </video>
        </div>
      )}
    </div>
  );
};
