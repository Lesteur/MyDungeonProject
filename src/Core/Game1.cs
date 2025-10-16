using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Graphics;
using Microsoft.Xna.Framework.Input;
using System;

namespace MyDungeonProject.Core
{
    /// <summary>
    /// Main game class.
    /// Uses a virtual resolution (virtualWidth x virtualHeight) to position objects.
    /// Rendering is scaled to the actual window while preserving aspect ratio.
    /// </summary>
    public class Game1 : Game
    {
        private GraphicsDeviceManager _graphics;
        private SpriteBatch _spriteBatch;

        // Virtual resolution we design for
        private readonly int virtualWidth = 1280;
        private readonly int virtualHeight = 720;

        // Player sprite and position (in virtual coordinates)
        private Texture2D _playerTexture = null!;
        private Vector2 _playerPosition;

        // Movement speed in virtual units per second
        private float _speed = 400f;

        // Input state
        private KeyboardState _previousKeyboardState;

        public Game1()
        {
            _graphics = new GraphicsDeviceManager(this);

            // Optional: let the OS set the initial window size (or set preferences)
            _graphics.PreferredBackBufferWidth = 1280;
            _graphics.PreferredBackBufferHeight = 720;
            _graphics.ApplyChanges();

            Content.RootDirectory = "Content";
            IsMouseVisible = true;

            Window.AllowUserResizing = true;
        }

        protected override void Initialize()
        {
            // Start player at center of virtual screen
            _playerPosition = new Vector2(virtualWidth / 2f, virtualHeight / 2f);

            base.Initialize();
        }

        protected override void LoadContent()
        {
            _spriteBatch = new SpriteBatch(GraphicsDevice);

            // Load the texture previously added to the Content pipeline
            // If you used MGCB and added "assets/player.png" with asset name "assets/player",
            // then call Content.Load<Texture2D>("assets/player")
            // Here we assume the asset name is "assets/player" (no extension)
            try
            {
                _playerTexture = Content.Load<Texture2D>("assets/player");
            }
            catch (Exception ex)
            {
                // Fallback: create a simple white texture to avoid crashes
                _playerTexture = new Texture2D(GraphicsDevice, 64, 64);
                Color[] data = new Color[64 * 64];
                for (int i = 0; i < data.Length; i++) data[i] = Color.White;
                _playerTexture.SetData(data);

                Console.WriteLine("Warning: player texture not found. Using placeholder. Exception: " + ex.Message);
            }
        }

        protected override void Update(GameTime gameTime)
        {
            // Exit on Escape
            var keyboard = Keyboard.GetState();
            if (keyboard.IsKeyDown(Keys.Escape))
                Exit();

            float dt = (float) gameTime.ElapsedGameTime.TotalSeconds;

            // Movement (WASD or arrow keys)
            Vector2 input = Vector2.Zero;
            if (keyboard.IsKeyDown(Keys.W) || keyboard.IsKeyDown(Keys.Up)) input.Y -= 1f;
            if (keyboard.IsKeyDown(Keys.S) || keyboard.IsKeyDown(Keys.Down)) input.Y += 1f;
            if (keyboard.IsKeyDown(Keys.A) || keyboard.IsKeyDown(Keys.Left)) input.X -= 1f;
            if (keyboard.IsKeyDown(Keys.D) || keyboard.IsKeyDown(Keys.Right)) input.X += 1f;

            if (input.LengthSquared() > 0f)
            {
                input.Normalize();
                _playerPosition += input * _speed * dt;

                // clamp to virtual viewport boundaries, considering origin at center of sprite
                float halfW = _playerTexture.Width / 2f;
                float halfH = _playerTexture.Height / 2f;

                _playerPosition.X = MathHelper.Clamp(_playerPosition.X, halfW, virtualWidth - halfW);
                _playerPosition.Y = MathHelper.Clamp(_playerPosition.Y, halfH, virtualHeight - halfH);
            }

            _previousKeyboardState = keyboard;

            base.Update(gameTime);
        }

        protected override void Draw(GameTime gameTime)
        {
            GraphicsDevice.Clear(Color.Black);

            // Compute scaling and viewport transform to keep aspect ratio
            int backBufferWidth = GraphicsDevice.Viewport.Width;
            int backBufferHeight = GraphicsDevice.Viewport.Height;

            float scaleX = (float)backBufferWidth / virtualWidth;
            float scaleY = (float)backBufferHeight / virtualHeight;
            float scale = Math.Min(scaleX, scaleY);

            // Calculate letterboxing offsets to center the virtual viewport
            int viewportWidth = (int)(virtualWidth * scale);
            int viewportHeight = (int)(virtualHeight * scale);
            int viewportX = (backBufferWidth - viewportWidth) / 2;
            int viewportY = (backBufferHeight - viewportHeight) / 2;

            // Option A: Use SpriteBatch with a scaling transform
            var transform = Matrix.CreateScale(scale, scale, 1f) *
                            Matrix.CreateTranslation(viewportX / scale, viewportY / scale, 0f);

            _spriteBatch.Begin(transformMatrix: transform, samplerState: SamplerState.PointClamp);

            // Draw player using virtual coordinates. Origin set to center of sprite.
            Vector2 origin = new Vector2(_playerTexture.Width / 2f, _playerTexture.Height / 2f);

            _spriteBatch.Draw(_playerTexture, _playerPosition, null, Color.White, 0f, origin, 1f, SpriteEffects.None, 0f);

            _spriteBatch.End();

            base.Draw(gameTime);
        }
    }
}
