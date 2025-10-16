using System;
using Microsoft.Xna.Framework;

namespace MyDungeonProject
{
    public static class Program
    {
        [STAThread]
        static void Main()
        {
            using var game = new MyDungeonProject.Core.Game1();
            game.Run();
        }
    }
}
