package com.junferno.badapple.listeners;

import org.bukkit.Location;
import org.bukkit.World;
import org.bukkit.entity.Creeper;
import org.bukkit.entity.EntityType;
import org.bukkit.event.EventHandler;
import org.bukkit.event.Listener;
import org.bukkit.event.entity.EntityExplodeEvent;
import org.bukkit.event.entity.ExplosionPrimeEvent;

public class ExplosionListener implements Listener {

	@EventHandler
	public void onExplosion(EntityExplodeEvent event) {
	    if (event.getEntity() instanceof Creeper) {
//	    	Creeper creeper = (Creeper) event.getEntity();
//	    	event.setCancelled(true);
//	    	Location l = creeper.getLocation();
//	    	World w = creeper.getWorld();
//	    	w.spawnEntity(l, EntityType.CREEPER);
//	    	creeper.remove();
//	    	newcreeper.ignite();
	    }
	}

//	@EventHandler
//	public void onExplosionPrime(ExplosionPrimeEvent event) {
//	    if (event.getEntity() instanceof Creeper) {
//	    	event.setCancelled(true);
//	    }
//	}

}
