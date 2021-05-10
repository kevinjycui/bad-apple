package com.junferno.badapple.commands;

import org.bukkit.command.Command;
import org.bukkit.command.CommandExecutor;
import org.bukkit.command.CommandSender;
import org.bukkit.entity.Player;

import com.junferno.badapple.BadApple;

public class SetPlayerCommand implements CommandExecutor {
		
	public SetPlayerCommand(BadApple plugin) {
		plugin.getCommand("player").setExecutor(this);
	}

	@Override
	public boolean onCommand(CommandSender sender, Command cmd, String label, String[] args) {
		if (!(sender instanceof Player)) {
			sender.sendMessage("Only players may execute this command!");
			return false;
		}
		
		Player p = (Player) sender;
		
		if (args.length > 1) {
			p.sendMessage("Invalid number of arguments");
			return false;
		}
		
		else if (args.length == 0) {
			if (BadApple.setPlayer(p)) {
				p.sendMessage("Player set to " + p.getDisplayName());
				return true;
			}
			p.sendMessage("Failed to set player to " + p.getDisplayName());
			return false;
		}
		
		for (Player player:p.getWorld().getPlayers()) {
			if (player.getPlayerListName().equals(args[0])) {
				if (!player.isOnline()) {
					p.sendMessage("Cannot set player to an offline player");
					return false;
				}
				else if (BadApple.setPlayer(player)) {
					p.sendMessage("Player set to " + player.getDisplayName());
					return true;
				}
				p.sendMessage("Failed to set player to " + player.getDisplayName());
				return false;
			}
		}
		
		return false;
	}

}
