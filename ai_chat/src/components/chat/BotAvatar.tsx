export const BotAvatar: React.FC = () => {
  return (
    <div className="mb-20 flex h-full w-full justify-center">
      <div className="flex aspect-square h-full items-center overflow-hidden rounded-full bg-blue-300">
        <video autoPlay className="h-full w-full object-cover" loop>
          <source src="placeholder.mp4" type="video/mp4" />
        </video>
      </div>
    </div>
  );
};
