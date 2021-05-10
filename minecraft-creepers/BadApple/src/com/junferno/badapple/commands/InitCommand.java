package com.junferno.badapple.commands;

import org.bukkit.Location;
import org.bukkit.command.Command;
import org.bukkit.command.CommandExecutor;
import org.bukkit.command.CommandSender;
import org.bukkit.entity.Player;

import com.junferno.badapple.BadApple;

public class InitCommand implements CommandExecutor {

	public InitCommand(BadApple plugin) {
		plugin.getCommand("init").setExecutor(this);
	}

	@Override
	public boolean onCommand(CommandSender sender, Command cmd, String label, String[] args) {
		if (!(sender instanceof Player)) {
			sender.sendMessage("Only players may execute this command!");
			return false;
		}

		Player p = (Player) sender;

		if (args.length != 1) {
			p.sendMessage("Invalid number of arguments");
			return false;
		}

		Location l = p.getLocation();

		try {
			int step = Integer.parseInt(args[0]);

			switch (step) {
			case 1:
				BadApple.setXY(l.getX(), l.getY(), l.getZ());
				p.sendMessage("Successfully set X and Z");
				break;
			case 2:
				if (!BadApple.setWH(l.getX(), l.getZ())) {
					p.sendMessage("Please set 1 before 2");					
					return false;
				}
				p.sendMessage("Successfully set W and H");	
				break;
			default:
				p.sendMessage("Undefined step");
				return false;
			}
		}
		catch (NumberFormatException e) {
			p.sendMessage("Invalid argument " + args[0]);
			return false;
		}

		return true;

	}
	
}
