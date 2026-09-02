using System.Collections.Generic;
using System.Threading;

namespace newClient.Comms;

public class Channel<T>
{
	private readonly Queue<T> m_collection = new Queue<T>();

	private readonly object syncRoot = new object();

	private readonly int m_millisecondsTimeout = 500;

	private readonly int m_maxCapacity;

	private bool IsCompleted;

	public int Count
	{
		get
		{
			lock (syncRoot)
			{
				return m_collection.Count;
			}
		}
	}

	public Channel(int capacity = 65535)
	{
		m_maxCapacity = capacity;
	}

	public bool TryEnqueue(T item)
	{
		lock (syncRoot)
		{
			if (IsCompleted)
			{
				return false;
			}
			while (m_collection.Count >= m_maxCapacity)
			{
				if (!Monitor.Wait(syncRoot, m_millisecondsTimeout) || IsCompleted)
				{
					return false;
				}
			}
			m_collection.Enqueue(item);
			if (m_collection.Count == 1)
			{
				Monitor.PulseAll(syncRoot);
			}
			return true;
		}
	}

	public bool TryDequeue(out T item)
	{
		lock (syncRoot)
		{
			if (IsCompleted)
			{
				item = default(T);
				return false;
			}
			while (m_collection.Count == 0)
			{
				if (!Monitor.Wait(syncRoot, m_millisecondsTimeout) || IsCompleted)
				{
					item = default(T);
					return false;
				}
			}
			item = m_collection.Dequeue();
			if (m_collection.Count + 1 == m_maxCapacity)
			{
				Monitor.PulseAll(syncRoot);
			}
			return true;
		}
	}

	public bool TryPeek(out T item)
	{
		lock (syncRoot)
		{
			if (IsCompleted || m_collection.Count == 0)
			{
				item = default(T);
				return false;
			}
			item = m_collection.Peek();
			return true;
		}
	}

	public void RemoveCount(int count)
	{
		lock (syncRoot)
		{
			for (int i = 0; i < count; i++)
			{
				m_collection.Dequeue();
			}
		}
	}

	public void CompleteAdding()
	{
		lock (syncRoot)
		{
			IsCompleted = true;
			m_collection.Clear();
		}
	}
}
